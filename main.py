import time,sys,threading
from copy import deepcopy
import pyperclip


from uilist import *
from calculation import *

def longest_list(lists):
    max_length = 0
    longest_list = []
    for lst in lists:
        current_length = len(lst)
        if current_length > max_length:
            max_length = current_length
            longest_list = lst
    return longest_list


Inf = float('inf')  # 无限大
# 输入框
class Input_box():
    def __init__(self):
        self.running = True
        # 综合数据
        #0:输入(列表),1:字符长度,2:尺寸类型,3:字符高度,
        self.result = [[], [], [], []]
        # 0:字符横坐标,1:字符纵坐标
        self.coordinate = [[],[],]
        history.append(deepcopy(self.result))
        # 光标显示位置
        self.px = 5
        self.py = 25
        # 光标位置
        self.place = 0
        # 显示开始位置
        self.start = 0
        self.top = 0
        # 光标长度
        self.long = 48
        # 式中位置
        self.lineup = 0

        self.cursor_show = True
        # 清除计算结果
        self.clear = True
        # 计算结果加入
        self.adding = False
        # 尾部追加优化
        self.left_and_right = []

    def __over(self, istr):
        over = 0
        if istr in all_symbols[0]:
            if istr in ['∫', '∮']:
                over = max(over, 20)
            else:
                over = max(over, 10)
        return over

    # 获取极点(顶,底)
    def get_pole(self, iplace): #iplace:self.place-1
        if iplace >= len(self.result[0]) or len(self.result[0])<1:
            return
        f = 0
        f_start, f_end = 0,0
        fltop = Inf
        flunder = 0
        # 向前遍历光标所在分数层的顶和底
        for i in range(iplace, -1, -1):
            if i == iplace: continue
            if self.result[0][i] == 'frac}':
                f += 1
            elif self.result[0][i] == 'frac{':
                if f != 0:
                    f -= 1
                else:
                    f_start = i + 1
                    break
            elif self.result[0][i] == '/' and f == 0:
                f_start = i + 1
                break
            # 排除特殊
            over = self.__over(self.result[0][i])
            # 顶
            fltop = min(fltop, self.coordinate[1][i] - over)
            # 底

            flunder = max(flunder, self.coordinate[1][i] + self.result[3][i] - over)

        # 向后遍历光标所在分数层的顶和底
        for i in range(iplace,len(self.result[0])):
            # 排除特殊
            over = self.__over(self.result[0][i])
            # 顶
            fltop = min(fltop, self.coordinate[1][i] - over)
            # 底
            flunder = max(flunder, self.coordinate[1][i] + self.result[3][i] - over)

            if self.result[0][i] == 'frac{':
                f -= 1
            elif self.result[0][i] == 'frac}':
                if f != 0:
                    f += 1
                else:
                    f_end = i + 1
                    break
            elif self.result[0][i] == '/' and f == 0:
                f_end = i + 1
                break
        top_over = fltop - self.coordinate[1][f_end-1]
        under_over = flunder - self.coordinate[1][f_end-1]-self.result[3][f_end-1]
        #print(self.result[0][f_start: f_end], f_start, f_end)
        return [fltop,flunder,f_start, f_end, top_over, under_over]

    #获得位置(上下标,根号等)
    def get_bplace(self, iplace):
        a = 0
        s = []

        left_u, left_d, left_r, left_ru, right_u, right_d, right_r, right_ru = 0,0,0,0,0,0,0,0
        left_f, right_f = 0,0
        for i in range(iplace):
            if self.result[0][i] == '^{':
                left_u += 1
            elif self.result[0][i] == '_{':
                left_d += 1
            elif self.result[0][i] == '√{':
                left_r += 1
            elif self.result[0][i] == '^√{':
                left_ru += 1
            elif self.result[0][i] == '^}':
                right_u += 1
            elif self.result[0][i] == '_}':
                right_d += 1
            elif self.result[0][i] == '√}':
                right_r += 1
            elif self.result[0][i] == '^√}':
                right_ru += 1
            elif self.result[0][i] == 'frac}':
                right_f += 1
            elif self.result[0][i] == 'frac{':
                left_f += 1
        """
        for i in range(iplace,len(self.result[0])):
            if self.result[0][i] == '/':
                s.append(3)
                break
            elif self.result[0][i] == 'frac}':
                s.append(4)
                break
            elif self.result[0][i] == 'frac{':
                break
        """

        if left_u - right_u >= 1:
            a = 1
            s.append(1)

        elif left_d - right_d >= 1:
            a = 1
            s.append(2)

        if left_r - right_r >= 1:
            s.append(5)

        if left_ru - right_ru >= 1:
            a = 1
            s.append(6)

        if left_f - right_f >= 1:
            s.append(3)

        if s == []:
            a = 0
            s.append(0)

        return [s, a, left_u, left_d, left_r, left_ru, left_f, right_u, right_d, right_r, right_ru, right_f]
        # 0:0中心,1上标,2下标,3分数内,5根号内,6根号上标,1:大小
    def __bplace(self, i, left_u, left_d, left_r, left_ru, left_f, left_m, right_u, right_d, right_r, right_ru, right_f, right_m):
        if self.result[0][i] == '^{':
            left_u += 1
        elif self.result[0][i] == '_{':
            left_d += 1
        elif self.result[0][i] == '√{':
            left_r += 1
        elif self.result[0][i] == '^√{':
            left_ru += 1
        elif self.result[0][i] == '^}':
            right_u += 1
        elif self.result[0][i] == '_}':
            right_d += 1
        elif self.result[0][i] == '√}':
            right_r += 1
        elif self.result[0][i] == '^√}':
            right_ru += 1
        elif self.result[0][i] == 'frac}':
            right_f += 1
        elif self.result[0][i] == 'frac{':
            left_f += 1
        elif self.result[0][i] in all_matrix_left:
            left_m +=1
        elif self.result[0][i] in all_matrix_right:
            right_m +=1
        a = 0
        if left_u - right_u >= 1:
            a = 1
        elif left_d - right_d >= 1:
            a = 1
        if left_ru - right_ru >= 1:
            a = 1
        return left_u, left_d, left_r, left_ru, left_f, left_m, right_u, right_d, right_r, right_ru, right_f, right_m, a

    # 输出显示
    def show(self):
        intervals = 0
        if not sliding:#滑动优化
            # 坐标
            self.coordinate = [[], []]
            #尺寸
            self.result[2] = []
            #高度
            self.result[3] = []

        # 光标在结尾时的竖直位置
        self.ENDYPLACE = 25

        # 矩阵尾括号显示长度调整
        matrix_long = []

        left_u, left_d, left_r, left_ru, left_f, left_m, right_u, right_d, right_r, right_ru, right_f, right_m = 0,0,0,0,0,0,0,0,0,0,0,0
        uadd,dadd = 0,0

        # ==================遍历准备=============================
        for i in range(len(self.result[0])):
            if sliding:continue #滑动优化
            left_u, left_d, left_r, left_ru, left_f, left_m, right_u, right_d, right_r, right_ru, right_f, right_m, a = \
                self.__bplace(i, left_u, left_d, left_r, left_ru, left_f, left_m, right_u, right_d, right_r, right_ru, right_f, right_m)

            self.result[2].append(a)
            # 初步调整相对位置
            self.lineup = 0

            # 高度
            if self.result[0][i] in all_brackets[0]:
                self.result[3].append(50 // (a + 1))
            elif self.result[0][i] in all_symbols[0]:
                if self.result[0][i] in ['∫', '∮']:
                    self.result[3].append(100 // (a + 1))
                else:
                    self.result[3].append(80 // (a + 1))
            elif self.result[0][i] in  ['_}','^}','^√}']:
                self.result[3].append(25)
            else:
                self.result[3].append(50 // (a + 1))

            # 宽度处理
            if self.result[0][i] == 'frac{':
                self.result[1][i] = 8//(a+1)
            elif self.result[0][i] == '/':
                dislocation_frac = 0
                self.result[1][i] = 0
                frac = 0
                for j in range(len(self.result[0][:i][::-1])):
                    if self.result[0][:i][::-1][j] == 'frac}':
                        frac +=1
                    elif self.result[0][:i][::-1][j] == 'frac{':
                        frac -=1
                        if frac == -1:
                            break
                    dislocation_frac += self.result[1][:i][::-1][j]
                self.result[1][i] -= dislocation_frac
            elif self.result[0][i] == 'frac}':
                self.result[1][i] = 8 // (a + 1)
                top, under = 0, 0
                fr = -1
                j = 0
                for j in range(len(self.result[0][:i][::-1])):
                    if self.result[0][:i][::-1][j] == 'frac{':
                        fr += 1
                    elif self.result[0][:i][::-1][j] == 'frac}':
                        fr -= 1
                    elif self.result[0][:i][::-1][j] == '/' and fr == -1:
                        top = -self.result[1][:i][::-1][j]
                        break
                    under += self.result[1][:i][::-1][j]

                if top - under > 0:
                    self.result[1][i] += (top - under)//2
                    self.result[1][i-j-1] += (top - under) - (top - under)//2
                elif top - under < 0 and self.result[0][i - j - 1] == '/':
                    fra = -1
                    k = i-j-1
                    for k in range(i-j-1, -1, -1):
                        if self.result[0][k] == 'frac{':
                            fra += 1
                            if fra == 0:
                                break
                        elif self.result[0][k] == 'frac}':
                            fra -= 1
                    if self.result[0][k] == 'frac{':
                        self.result[1][k] = 8 // (a + 1)
                        self.result[1][i - j - 1] -= (under - top) //2
                        self.result[1][k] += (under - top) //2
            elif self.result[0][i] == '^{' and i != 0 and i != len(self.result[0]) - 1:
                self.result[1][i] = 0
                for v in range(len(self.result[0][i + 1:])):
                    if self.result[0][i + 1:][v] == '^}':
                        self.result[1][i + 1 + v] = 0
                        break
                if self.result[0][i - 1] == '_}':
                    dislocation_u = 0
                    sink_d = 0
                    for j in range(len(self.result[0][:i - 1][::-1])):
                        if self.result[0][:i-1][::-1][j] == '_}':
                            sink_d += 1
                        elif self.result[0][:i-1][::-1][j] == '_{':
                            sink_d -= 1
                            if sink_d == -1:
                                break
                        dislocation_u += self.result[1][:i - 1][::-1][j]
                    self.result[1][i] -= dislocation_u
                    u, v = 0, 0
                    float_u = 0
                    for v in range(len(self.result[0][i + 1:])):
                        if self.result[0][i + 1:][v] == '^{':
                            float_u +=1
                        elif self.result[0][i + 1:][v] == '^}':
                            float_u -= 1
                            if float_u == -1:
                                self.result[1][i + 1 + v] = 0
                                break
                        u += self.result[1][i + 1:][v]
                    if dislocation_u > u and float_u == -1:
                        self.result[1][i + 1 + v] += dislocation_u - u
            elif self.result[0][i] == '_{' and i != 0 and i != len(self.result[0]) - 1:
                self.result[1][i] = 0
                for v in range(len(self.result[0][i + 1:])):
                    if self.result[0][i + 1:][v] == '_}':
                        self.result[1][i + 1 + v] = 0
                        break
                if self.result[0][i - 1] == '^}':
                    dislocation_d = 0
                    float_u = 0
                    for j in range(len(self.result[0][:i - 1][::-1])):
                        if self.result[0][:i - 1][::-1][j] == '^}':
                            float_u += 1
                        elif self.result[0][:i - 1][::-1][j] == '^{':
                            float_u -=1
                            if float_u == -1:
                                break
                        dislocation_d += self.result[1][:i - 1][::-1][j]
                    self.result[1][i] -= dislocation_d
                    d, v = 0, 0
                    sink_d = 0
                    for v in range(len(self.result[0][i + 1:])):
                        if self.result[0][i + 1:][v] == '_{':
                            sink_d +=1
                        elif self.result[0][i + 1:][v] == '_}':
                            sink_d -=1
                            if sink_d == -1:
                                self.result[1][i + 1 + v] = 0
                                break
                        d += self.result[1][i + 1:][v]
                    if dislocation_d > d and sink_d == -1:
                        self.result[1][i + 1 + v] += dislocation_d - d
            elif self.result[0][i] == '^√}':
                dislocation_root = 0
                self.result[1][i] = 0
                for j in range(len(self.result[0][:i][::-1])):
                    if self.result[0][:i][::-1][j] == '^√{':
                        if self.result[3][:i][::-1][j] < 40:ar = 1
                        else:ar = 0
                        break
                    dislocation_root += self.result[1][:i][::-1][j]
                if dislocation_root >= (45 - 20*a) //(ar+1):
                    dislocation_root = (45 - 20*a)//(ar+1)
                self.result[1][i] -= dislocation_root
            elif self.result[0][i] in all_special_fuc[0]:
                if i+1 < len(self.result[0]):
                    if self.result[0][i+1] not in ['frac{','^{','_{','(','^√{','√{','[','{']:
                        self.result[1][i] = all_special_fuc[1][all_special_fuc[0].index(self.result[0][i])]//(a+1)+5//(a+1)
                    else:
                        self.result[1][i] = all_special_fuc[1][all_special_fuc[0].index(self.result[0][i])]//(a+1)

                # 上下标处理
            elif self.result[0][i] == r'\\' and left_m-right_m == 0:
                dislocation = 0
                case = 0
                for j in range(len(self.result[0][:i][::-1])):
                    if self.result[0][:i][::-1][j] == r'\\' and case == 0:
                        self.result[1][i] = dislocation
                        break
                    elif self.result[0][:i][::-1][j] in all_matrix_left:
                        if case ==0:
                            break
                        else:
                            case +=1
                    elif self.result[0][:i][::-1][j] in all_matrix_right:
                        case -=1
                    dislocation -= self.result[1][:i][::-1][j]
                else:
                    self.result[1][i] = dislocation
            elif self.result[0][i] in all_matrix_left:
                for k in range(len(all_matrix_left)):
                    if all_matrix_left[k] == self.result[0][i]:
                        cases = 0
                        total = 0
                        # 获得每格宽度
                        inter_lis = [[]]
                        for j in range(len(self.result[0][i:])):
                            if self.result[0][i:][j] in all_matrix_right:
                                cases -= 1
                            elif self.result[0][i:][j] in all_matrix_left:
                                cases += 1
                            if j == 0:continue
                            if cases == 1:
                                if self.result[0][i:][j] == r'&':
                                    inter_lis[-1].append(total)
                                    total = -self.result[1][i:][j]
                                elif self.result[0][i:][j] == r'\\':
                                    inter_lis[-1].append(total)
                                    inter_lis.append([])
                                    total = -self.result[1][i:][j]

                            elif cases == 0:
                                inter_lis[-1].append(total)
                                break
                            total += self.result[1][i:][j]
                        # 获得每列最大宽度
                        max_totals = []
                        for m in range(len(longest_list(inter_lis))):
                            max_total = 0
                            for n in range(len(inter_lis)):
                                if m < len(inter_lis[n]):
                                    max_total = max(max_total, inter_lis[n][m])
                            max_totals.append(max_total)
                        # 对齐每列
                        n, m = 0, 0
                        for j in range(len(self.result[0][i:])):
                            if self.result[0][i:][j] in all_matrix_right:
                                cases -= 1
                            elif self.result[0][i:][j] in all_matrix_left:
                                cases += 1
                            if j == 0:
                                if max_totals != []:
                                    self.result[1][i] = (max_totals[n] - inter_lis[m][n])//2 + all_matrix[1][k*2]
                                continue
                            if cases == 1:
                                if self.result[0][i:][j] == r'&':
                                    # 调控居中
                                    self.result[1][i + j] = max_totals[n] - inter_lis[m][n] - (max_totals[n] - inter_lis[m][n])//2 + 23\
                                                            + (max_totals[n+1] - inter_lis[m][n+1])//2
                                    n += 1
                                elif self.result[0][i:][j] == r'\\':
                                    # 调控居中
                                    nextline = 0
                                    if inter_lis[m+1] != []:
                                        nextline = (max_totals[0] - inter_lis[m+1][0])//2
                                    self.result[1][i + j] = (-sum(max_totals[:len(inter_lis[m])]) - 23*(len(inter_lis[m])-1)\
                                                            + (max_totals[n] - inter_lis[m][n]) - (max_totals[n] - inter_lis[m][n])//2\
                                                            + nextline)
                                    n = 0
                                    m += 1

                            elif cases == 0:
                                # 调控居中
                                self.result[1][i + j] = (sum(max_totals[len(inter_lis[m])-1:]) + 23 * (len(max_totals) - len(inter_lis[m])) \
                                                        - inter_lis[m][n] \
                                                        - (max_totals[n] - inter_lis[m][n])//2 \
                                                         + all_matrix[1][k*2 + 1])
                                break
                        break


            # 根号上标，上标，下标处理
            """"
            if left_u - right_u >= 1 or (left_u - right_u == 0 and self.result[0][i] =='^}'):
                if not (left_u - right_u == 1 and self.result[0][i] == '^{'):
                    self.lineup += -5 - uadd
                if left_d - right_d >= 1:
                    self.lineup += 25
            elif left_d - right_d >= 1 or (left_d - right_d == 0 and self.result[0][i] =='_}'):
                if not (left_d - right_d == 1 and self.result[0][i] == '_{'):
                    self.lineup += 25 + dadd
                    pass
            elif left_ru - right_ru >= 1 or (left_ru - right_ru == 0 and self.result[0][i] =='^√}'):
                if not (left_ru - right_ru == 1 and self.result[0][i] == '^√{'):
                    self.lineup += -5
            
            
            if self.result[0][i] in all_symbols[0]:
                if left_u - right_u == 0:
                    if self.result[0][i] in ['∫', '∮']:uadd = 15
                    else:uadd = 5
                elif left_d - right_d == 0:
                    if self.result[0][i] in ['∫', '∮']:dadd = 25
                    else:dadd = 5
            else:
                uadd,dadd = 0,0
                self.lineup = 0
            """
            show_yplace = 25 + self.lineup
            self.coordinate[1].append(show_yplace)

        #高度调整
        if not sliding:#滑动优化
            self.y_place()

        if self.result[0] != []:
            # 顶端对齐边框
            top_def = self.__pole(None, None, 0)[0] + self.top - 25
            for i in range(len(self.result[0])):
                self.coordinate[1][i] -= top_def
            self.ENDYPLACE -= top_def

        #==================遍历显示=============================
        for i in range(len(self.result[0])):
            a = self.result[2][i]
            # 显示字符
            show_xplace, show_yplace = 5 + intervals - self.start, self.coordinate[1][i]+a*3
            self.coordinate[0].append(show_xplace)

            intervals += self.result[1][i]

            #优化显示
            #if show_xplace > size[0] or show_xplace + self.result[1][i]< 0:continue
            correction = 0

            # 数字
            if self.result[0][i] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
                screen.blit(f_number[a].render(self.result[0][i], [True,False][a], (0, 0, 0), None), (show_xplace, show_yplace + a * 5 - 15))
                '''
                num = int(self.result[0][i])
                if num == 0:

                    screen.blit(nums[a], (show_xplace, show_yplace - a*3),
                                ((22 * (10 - 1) + 10 // 4) // (a + 1), 0, 22 // (a + 1), 240 // (a + 1)))

                else:
                    
                    #screen.blit(nums[a], (show_xplace, show_yplace - a*3),
                    #            ((22 * (num - 1) + num // 4) // (a + 1), 0, 22 // (a + 1), 240 // (a + 1)))
                    
                '''

            elif self.result[0][i] == '°':
                screen.blit(f_number[a].render('°', False, (0, 0, 0), None),
                            (show_xplace, show_yplace + a * 5 - 15))
                #screen.blit(nums[a], (show_xplace, show_yplace),
                #            ((220 + 10 // 4) // (a + 1), 0, 18 // (a + 1), 240 // (a + 1)))
            # 点
            elif self.result[0][i] in all_points[0]:
                for k in range(len(all_points[0])):
                    if all_points[0][k] == self.result[0][i]:
                        screen.blit(point[a], (show_xplace, show_yplace), (
                        (correction + k // 2 * 5 + k // 3 * 5) // (a + 1), 0, all_points[1][k] // (a + 1), 50))
                        break
                    correction += all_points[1][k]
            # 英文小写字母
            elif self.result[0][i] in all_el_letters[0]:
                '''
                screen.blit(f_character[a].render(self.result[0][i], [True, False][a], (0, 0, 0), None),
                            (show_xplace, show_yplace + a * 5 - 15))
                '''
                for k in range(len(all_el_letters[0])):
                    if el_letters[k + 97] == self.result[0][i]:
                        screen.blit(letters[a], (show_xplace, show_yplace-1*a),
                                    ((8 + correction) // (a + 1), 5, all_el_letters[1][k] // (a + 1), 50))
                        break
                    correction += all_el_letters[1][k]
            # 英文大写字母
            elif self.result[0][i] in all_eu_letters[0]:
                for k in range(len(all_eu_letters[0])):
                    if eu_letters[k + 97] == self.result[0][i]:
                        screen.blit(uletters[a], (show_xplace, show_yplace),
                                    ((10 + correction) // (a + 1), 5, all_eu_letters[1][k] // (a + 1), 50))
                        break
                    correction += all_eu_letters[1][k]
            # 希腊小写字母
            elif self.result[0][i] in all_gl_letters[0]:
                for k in range(len(all_gl_letters[0])):
                    if all_gl_letters[0][k] == self.result[0][i]:
                        screen.blit(gletters[a], (show_xplace, show_yplace-1*a),
                                    ((8 + correction) // (a + 1), 5, all_gl_letters[1][k] // (a + 1), 50))
                        break
                    correction += all_gl_letters[1][k]
            # 希腊大写字母
            elif self.result[0][i] in all_gu_letters[0]:
                for k in range(len(all_gu_letters[0])):
                    if all_gu_letters[0][k] == self.result[0][i]:
                        screen.blit(guletters[a], (show_xplace, show_yplace),
                                    ((8 + correction) // (a + 1), 5, all_gu_letters[1][k] // (a + 1), 50))
                        break
                    correction += all_gu_letters[1][k]
            # 运算符
            elif self.result[0][i] in all_operators[0]:
                for k in range(len(all_operators[0])):
                    if all_operators[0][k] == self.result[0][i]:
                        screen.blit(operator[a], (show_xplace, 5 + show_yplace-a*3),
                                    ((8 + correction) // (a + 1), 14 - (a * 5), all_operators[1][k] // (a + 1), 50))
                        break
                    correction += all_operators[1][k]
            # 关系符
            elif self.result[0][i] in all_relations[0]:
                for k in range(len(all_relations[0])):
                    if all_relations[0][k] == self.result[0][i]:
                        screen.blit(relation[a], (show_xplace, show_yplace - 5),
                                    ((8 + correction) // (a + 1), 3, all_relations[1][k] / (a + 1), 50))
                        if i > 0 and self.result[0][i] == '=':
                            if self.result[0][i - 1] == '=':
                                pygame.draw.rect(screen, (255, 255, 255), (
                                show_xplace - all_relations[1][k] // (a + 1), 23 - 5 + show_yplace - a * 13,
                                all_relations[1][k] // (a + 1) * 2, 10 // (a + 1)), 0)
                                pygame.draw.rect(screen, (0, 0, 0), (
                                show_xplace - all_relations[1][k] // (a + 1), 23 - 5 + show_yplace - a * 13,
                                all_relations[1][k] // (a + 1) * 2, 2 // (a + 1)), 0)
                                pygame.draw.rect(screen, (0, 0, 0), (show_xplace - all_relations[1][k] // (a + 1),
                                                                     23 - 5 + show_yplace - a * 13 + 10 // (
                                                                                 a + 1) - 2 // (a + 1),
                                                                     all_relations[1][k] // (a + 1) * 2, 2 // (a + 1)),
                                                 0)
                        break
                    correction += all_relations[1][k]
            # 括号
            elif self.result[0][i] in all_brackets[0]:
                for k in range(len(all_brackets[0])):
                    if all_brackets[0][k] == self.result[0][i]:
                        screen.blit(bracket[a], (show_xplace, -5 + show_yplace - a*3),
                                    ((correction) // (a + 1), -5, all_brackets[1][k] // (a + 1), 60))
                        break
                    correction += all_brackets[1][k]
            # 大型运算符
            elif self.result[0][i] in all_symbols[0]:
                for k in range(len(all_symbols[0])):
                    if all_symbols[0][k] == self.result[0][i]:
                        if self.result[0][i] in ['∫', '∮']:
                            screen.blit(symbol, (show_xplace, -20 + show_yplace),
                                        ((correction + 5) // (a + 1), 5, all_symbols[1][k] // (a + 1), 100))
                            break
                        else:
                            screen.blit(symbol, (show_xplace, -20 + show_yplace),
                                        ((5 + correction) // (a + 1), 5, all_symbols[1][k] // (a + 1), 80))
                            break
                    correction += all_symbols[1][k]
            # 箭头
            elif self.result[0][i] in all_arrows[0]:
                for k in range(len(all_arrows[0])):
                    if all_arrows[0][k] == self.result[0][i]:
                        screen.blit(arrow[a], (show_xplace, -5 + show_yplace),
                                    ((4 + k // 2 * 5 + correction) // (a + 1), -5, all_arrows[1][k] / (a + 1), 60))
                        break
                    correction += all_arrows[1][k]
            # 根号
            elif self.result[0][i] == '√{':
                # 根号处理
                rootlong = 0
                root_long = 0
                ro = 0
                for x in range(len(self.result[0][i:])):
                    if root_long == 0:
                        rootlong += self.result[1][i:][x]
                    if self.result[0][i:][x] == '√{':
                        ro += 1
                    elif self.result[0][i:][x] == '√}':
                        ro -= 1
                        if ro == 0:
                            root_long = rootlong
                            break
                pygame.draw.rect(screen, (0, 0, 0),
                            (show_xplace + 38 // (a + 1), 2 + show_yplace - a*3 - a*2,
                             root_long - 38 // (a + 1), 2 // (a + 1)), 0)

                screen.blit(root_h(self.result[3][i]-4+ a*4)[a],
                            (show_xplace, -1 + show_yplace - a*3),
                            (0, 1, 38 // (a + 1), self.result[3][i]))
            # 分数线长
            elif self.result[0][i] == 'frac{':
                fr = 0
                fraclong = 0
                frac_long = 0
                for x in range(len(self.result[0][i:])):
                    fraclong += self.result[1][i:][x]
                    if self.result[0][i:][x] == 'frac{':
                        fr += 1
                    elif self.result[0][i:][x] == '/' and fr == 1:
                        frac_long = fraclong - self.result[1][i:][x]
                        fraclong = 0

                    elif self.result[0][i:][x] == 'frac}':
                        fr -= 1
                        if fr == 0:
                            frac_long = max(frac_long, fraclong)
                            break

                pygame.draw.rect(screen, (0, 0, 0),
                                 (show_xplace +4 // (a + 1), 2 - 5 + show_yplace - a*3 + 25 // (a + 1),
                                  frac_long, 2 // (a + 1)), 0)
            # 特殊函数
            elif self.result[0][i] in all_special_fuc[0]:
                for k in range(len(all_special_fuc[0])):
                    if all_special_fuc[0][k] == self.result[0][i]:
                        screen.blit(special_fuc[a], (show_xplace, show_yplace),
                                    ((8 + correction) // (a + 1), 10 - 2*a, all_special_fuc[1][k] // (a + 1), 50))
                        break
                    correction += all_special_fuc[1][k]
            elif self.result[0][i] in all_special_fuc2[0]:
                for k in range(len(all_special_fuc2[0])):
                    if all_special_fuc2[0][k] == self.result[0][i]:
                        screen.blit(special_fuc2[a], (show_xplace, show_yplace),
                                    ((8 + correction) // (a + 1), 10 - 2*a, all_special_fuc2[1][k] // (a + 1), 50))
                        break
                    correction += all_special_fuc2[1][k]
            #其他符号
            elif self.result[0][i] in all_others[0]:
                for k in range(len(all_others[0])):
                    if all_others[0][k] == self.result[0][i]:
                        screen.blit(others[a], (show_xplace, show_yplace-2*a),
                                    ((8 + correction) // (a + 1), 10  - 4*a, all_others[1][k] // (a + 1), 50))
                        break
                    correction += all_others[1][k]
            # 矩阵
            elif self.result[0][i] in all_matrix[0]:
                for k in range(len(all_matrix[0])):
                    if all_matrix[0][k] == self.result[0][i]:
                        if k%2 == 0:#头
                            up_hmatrix, down_hmatrix, end = self.__pole(all_matrix[0][k], all_matrix[0][k+1], i+1)
                            matrix_long.append((up_hmatrix, down_hmatrix))
                            if all_matrix[0][k] == r'\begin{bmatrix}':
                                pygame.draw.rect(screen, (0, 0, 0),
                                                 (show_xplace + 5,
                                                  matrix_long[-1][0] + 2, 10, 4), 0)
                                pygame.draw.rect(screen, (0, 0, 0),
                                                 (show_xplace + 5,
                                                  matrix_long[-1][0] + 2, 4,
                                                  matrix_long[-1][1] - matrix_long[-1][0] - 5), 0)
                                pygame.draw.rect(screen, (0, 0, 0),
                                                 (show_xplace + 5,
                                                  matrix_long[-1][1] - 7, 10, 4), 0)
                            elif all_matrix[0][k] == r'\begin{vmatrix}':
                                pygame.draw.rect(screen, (0, 0, 0),
                                                 (show_xplace + 5,
                                                  matrix_long[-1][0] + 2, 3,
                                                  matrix_long[-1][1] - matrix_long[-1][0] - 5), 0)
                            else:
                                screen.blit(matrix_h(down_hmatrix - up_hmatrix), (show_xplace, up_hmatrix),
                                        (correction, 2, all_matrix[1][k], down_hmatrix - up_hmatrix))

                        elif all_matrix[0][k] != r'\end{cases}':# 尾
                            if all_matrix[0][k] == r'\end{bmatrix}':
                                pygame.draw.rect(screen, (0, 0, 0),
                                                 (show_xplace + self.result[1][i] - all_matrix[1][k] + 4,
                                                  matrix_long[-1][0] + 2, 10, 4), 0)
                                pygame.draw.rect(screen, (0, 0, 0),
                                                 (show_xplace + self.result[1][i] - all_matrix[1][k] + 10, matrix_long[-1][0] + 2, 4, matrix_long[-1][1] - matrix_long[-1][0] - 5), 0)
                                pygame.draw.rect(screen, (0, 0, 0),
                                                 (show_xplace + self.result[1][i] - all_matrix[1][k] + 4,
                                                  matrix_long[-1][1] - 7, 10, 4), 0)
                            elif all_matrix[0][k] == r'\end{vmatrix}':
                                pygame.draw.rect(screen, (0, 0, 0),
                                                 (show_xplace + self.result[1][i] - all_matrix[1][k] + 5, matrix_long[-1][0] + 2, 3, matrix_long[-1][1] - matrix_long[-1][0] - 5), 0)
                            else:
                                screen.blit(matrix_h(matrix_long[-1][1] - matrix_long[-1][0]), (show_xplace + self.result[1][i] - all_matrix[1][k], matrix_long[-1][0]),
                                        (correction, 2, all_matrix[1][k], matrix_long[-1][1] - matrix_long[-1][0]))
                            matrix_long.pop(-1)
                        else:
                            matrix_long.pop(-1)

                        break

                    if all_matrix[0][k] != r'\end{cases}':
                        correction += all_matrix[1][k]
                    elif all_matrix[0][k] == r'\end{cases}':
                        correction += 7
            # 文字
            elif self.result[0][i] == '[ANSWER]':
                screen.blit(ANSWER, (show_xplace, show_yplace))
            elif '[ERROR]' in self.result[0][i]:
                if self.result[0][i][7:] in ['恒成立','无解','计算失败']:
                    screen.blit(f4.render(self.result[0][i][7:], 1, (0, 0, 0)), (show_xplace, show_yplace))
                else:
                    screen.blit(f4.render(self.result[0][i][7:], 1, (255, 0, 0)), (show_xplace, show_yplace))


    # 找整体的顶和底
    def __pole(self, istr, istr_n, i):
        ro = 0
        up_h, down_h = Inf, -Inf
        x = 0
        # 找顶和底（默认从i位置开始，使用时以左括号为开始,不包含左括号）
        for x in range(len(self.result[0][i:])):
            over = self.__over(self.result[0][i:][x])
            up_h = min(up_h, self.coordinate[1][i:][x] - over)
            down_h = max(down_h, self.coordinate[1][i:][x] + self.result[3][i:][x] - over)

            if self.result[0][i:][x] == istr:
                ro += 1
            elif self.result[0][i:][x] == istr_n:
                ro -= 1
                if ro == -1:
                    break
        end = i+x
        return up_h, down_h, end

    # 竖直方向排版
    '''使用影响域即将字符看作独立的方块检测其上顶和下底是否和其他字符冲突以达到排版效果'''
    def y_place(self):
        path = []
        # 分数显示位置

        # 栈方法寻找分数层并确定处理顺序
        for i in range(len(self.result[0])):
            if i > 0:
                if self.result[0][i-1] == 'frac{':
                    ret = self.get_pole(i)
                    f_start, f_end = ret[2], ret[3]
                    if [f_start, f_end] not in path and f_start < f_end:
                        if f_end >= len(self.result[0]):return
                        ret = self.get_pole(f_end)
                        path.append([ret[2], ret[3]])
                        path.append([f_start, f_end])


        path = path[::-1]
        place_path = []
        # 分层逐级调整
        for f in range(0, len(path), 2):
            f_start, f_end, f_start_n, f_end_n = path[f][0], path[f][1], path[f+1][0], path[f+1][1]

            # 上下标,根号位置
            self.float_sink_place(f_start, f_end, place_path, [])
            self.root_place(f_start, f_end, place_path)
            for r in range(f_start, f_end):place_path.append(r)

            self.float_sink_place(f_start_n, f_end_n, place_path, [])
            self.root_place(f_start_n, f_end_n, place_path)
            for r in range(f_start_n, f_end_n):place_path.append(r)

            fltop, flunder = self.get_pole(f_start_n)[0], self.get_pole(f_start)[1]
            if fltop != Inf:
                # 是否位置冲突
                if fltop != flunder or (flunder - 25 // (a+1)) != self.coordinate[1][path[f][0]-1]:
                    a = self.result[2][f_start]
                    dif = fltop - flunder
                    affected_area = [0, len(self.result[0])]
                    # 向外找影响域
                    for af in range(len(path)):
                        if path[af][0] < path[f][0] and path[f][1] < path[af][1]:
                            affected_area = path[af]
                            break

                    # 根据影响域调节下层和中层
                    '''
                    上层
                    ----中层
                    下层
                    '''
                    de = (flunder - 25 // (a+1)) - self.coordinate[1][path[f][0]-1]
                    for i in range(affected_area[0], affected_area[1]):
                        # 上层
                        if path[f][0] <= i < path[f][1]:
                            continue
                        # 下层
                        if path[f+1][0] <= i < path[f+1][1]:
                            self.coordinate[1][i] -= dif
                            continue
                        # 中层
                        self.coordinate[1][i] += de

        # 最外层
        if len(self.result[0]) != 0:
            self.float_sink_place(0, len(self.result[0]), place_path, [])
            self.root_place(0, len(self.result[0]), place_path)
            self.matrix_place()
            self.newline_place()

    # 根号显示位置
    def root_place(self, start, end, path):
        # 由内向外逐层递加
        for i in range(end-1, start-1, -1):
            if i in path: continue
            a = self.result[2][i]

            if self.result[0][i] == '√{':
                up_h, down_h, end = self.__pole('√{', '√}', i+1)
                max_height = down_h - up_h

                if max_height < 50//(a+1): max_height = 50//(a+1)
                self.coordinate[1][i] = up_h - 5//(a+1)
                self.result[3][i] = max_height + 8//(a+1)

    # 寻找上下标归属
    def __find_owner(self, i):
        sub, sup= 0,0
        #print(self.result[0][i],i,'iii', len(self.result[0][:i+1]), len(self.result[0][i::-1]))
        for v in range(i):
            if self.result[0][i-v] == '^{':sub += 1
            elif self.result[0][i-v] == '^}':sub -= 1
            elif self.result[0][i-v] == '_{':sup += 1
            elif self.result[0][i-v] == '_}':sup -= 1
            #print(sub,sup,i-v-1)
            if ((sub == 1 and sup == 0)or(sub == 0 and sup == 1))and i-v-1 >= 0:
                    if self.result[0][i-v-1] not in ['_}', '_{', '^}','^{']:
                        #print(self.result[0][i-v-1], i-v-1)
                        return i-v-1
        return None

    # 上下标显示位置
    def float_sink_place(self, start, end, path, fs_path):
        for i in range(start, end):
            if i in path: continue
            if i in fs_path: continue
            if self.result[0][i] == '^{':
                self.float_sink_place(i+1, end, path, fs_path)# 递归，从内向外调整
                up_h, down_h, fs_end = self.__pole('^{', '^}', i+1)

                for r in range(i+1, fs_end+1): fs_path.append(r)
                owner = self.__find_owner(i)
                if owner != None:
                    up_dif = up_h - (self.coordinate[1][owner] - self.__over(self.result[0][owner]))
                    under_dif = down_h - (self.coordinate[1][owner]+self.result[3][owner]//2)
                else:
                    up_dif = up_h - self.coordinate[1][i]
                    under_dif = down_h - (self.coordinate[1][i]+50//2)
                if up_dif > 0: #对齐上方
                    for j in range(i+1,fs_end+1):
                        if (j >= len(self.coordinate[1])):break
                        self.coordinate[1][j] -= up_dif
                else:up_dif = 0
                if under_dif-up_dif > 0:#防止上标内容过高挤压下方内容
                    for j in range(i+1,fs_end+1):self.coordinate[1][j] -= under_dif-up_dif

            elif self.result[0][i] == '_{':
                self.float_sink_place(i+1, end, path, fs_path)
                up_h, down_h, fs_end = self.__pole('_{', '_}', i+1)
                for r in range(i + 1, fs_end+1): fs_path.append(r)
                owner = self.__find_owner(i)
                if owner != None:dif = (self.coordinate[1][owner] + self.result[3][owner] // 2) - up_h
                else:dif = (self.coordinate[1][i]+50//2) - up_h
                if dif > 0:#防止下标内容过高挤压上方内容
                    for j in range(i+1,fs_end+1):self.coordinate[1][j] += dif - 5
            # 修正根号上标
            elif self.result[0][i] == '^√{':
                self.float_sink_place(i+1, end, path, fs_path)
                up_h, down_h, fs_end = self.__pole('^√{', '^√}', i+1)
                for r in range(i + 1, fs_end + 1): fs_path.append(r)
                owner = i
                if owner != None:dif = down_h - (self.coordinate[1][owner] + self.result[3][owner] // 2)
                else:dif = down_h - (self.coordinate[1][i] + 50 // 2)
                if dif > 0:  # 防止上标内容过高挤压下方内容
                    for j in range(i + 1, fs_end + 1): self.coordinate[1][j] -= dif

            elif self.result[0][i] in ['^}', '_}', '^√}']:break

    # 矩阵显示位置
    def matrix_place(self,start=0):
        if len(self.result[0]) < 2:return
        path = [] # 栈方法由内到外逐步调整
        for i in range(start, len(self.result[0])):
            if self.result[0][i] in all_matrix_left:
                for k in range(len(all_matrix_left)):
                    if all_matrix_left[k] == self.result[0][i]:
                        up_h, down_h, end = self.__pole(all_matrix_left[k], all_matrix_right[k], i + 1)
                        path.append([i, end])
        path = path[::-1]
        for lis in path:
            # 由内到外逐步调整
            if lis[1] + 1 > len(self.result[0]):return
            self.__matrixline(lis[0] + 1, lis[1] + 1)
            up_h, down_h, end = self.__pole(self.result[0][lis[0]], self.result[0][lis[1]], lis[0] + 1)
            df = (down_h - up_h)//2-50//2
            adf = up_h - self.coordinate[1][lis[0]]
            for j in range(lis[0] + 1,lis[1] + 1):
                self.coordinate[1][j] -= (df+adf)

    # 矩阵内部换行
    def __matrixline(self, start, end):
        past = start-1
        case = 1
        mpath = []
        for i in range(start, end):
            if self.result[0][i] in all_matrix_left:
                case += 1
            elif self.result[0][i] in all_matrix_right:
                case -= 1
                if case == 0:
                    mpath.append([past+1,i+1])
                    break
            if case > 1: continue
            if self.result[0][i] == r'\\':
                mpath.append([past+1,i+1])
                past = i

        if len(mpath) >= 2:
            for j in range(len(mpath)-1):
                up_h, down_h = Inf, -Inf
                up_h_n, down_h_n = Inf, -Inf
                for x in range(mpath[j][0], mpath[j][1]):
                    over = self.__over(self.result[0][x])
                    up_h = min(up_h, self.coordinate[1][x] - over)
                    down_h = max(down_h, self.coordinate[1][x] + self.result[3][x] - over)
                for y in range(mpath[j + 1][0],mpath[j + 1][1]):
                    over = self.__over(self.result[0][y])
                    up_h_n = min(up_h_n, self.coordinate[1][y] - over)
                    down_h_n = max(down_h_n, self.coordinate[1][y] + self.result[3][y] - over)

                # 前后底、顶作差得高度差
                dif = down_h - up_h_n
                # 防止上方内容过高挤压下方内容
                for i in range(mpath[j + 1][0],mpath[j + 1][1]):
                    self.coordinate[1][i] += dif

    # 换行
    def newline_place(self):
        up_h, down_h, fs_end = None,None,None
        past = -1
        in_matrix = 0
        npath = []
        self.ENDYPLACE = self.coordinate[1][0]
        for i in range(len(self.result[0])):
            # 跳过矩阵中的回车，单独处理
            if self.result[0][i] in all_matrix_left:
                in_matrix += 1
            elif self.result[0][i] in all_matrix_right:
                in_matrix -= 1
            # 处理外部回车
            elif self.result[0][i] == r'\\' and in_matrix == 0:
                npath.append([past + 1, i + 1])
                past = i
        # 防止上方内容过高挤压下方内容
        npath.append([past + 1, len(self.result[0])])
        dif = Inf
        if len(npath) > 1:
            for j in range(len(npath)-1):
                up_h, down_h = Inf, -Inf
                up_h_n, down_h_n = Inf, -Inf
                for x in range(npath[j][0], npath[j][1]):
                    over = self.__over(self.result[0][x])
                    up_h = min(up_h, self.coordinate[1][x] - over)
                    down_h = max(down_h, self.coordinate[1][x] + self.result[3][x] - over)
                for y in range(npath[j + 1][0], npath[j + 1][1]):
                    over = self.__over(self.result[0][y])
                    up_h_n = min(up_h_n, self.coordinate[1][y] - over)
                    down_h_n = max(down_h_n, self.coordinate[1][y] + self.result[3][y] - over)
                # 前后底、顶作差得高度差
                dif = down_h - up_h_n
                for i in range(npath[j + 1][0],npath[j + 1][1]):
                    self.coordinate[1][i] += dif

                if dif <= 0:
                    self.ENDYPLACE = down_h
                else:
                    self.ENDYPLACE = self.coordinate[1][npath[j + 1][0]]
    # 是否可回车
    def __allowed_enter(self, character):
        if self.left_and_right == []:
            self.left_and_right = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        left_u, left_d, left_r, left_ru, left_f, left_m, right_u, right_d, right_r, right_ru, right_f, right_m, a= self.left_and_right

        if character == '^{':
            left_u += 1
        elif character == '_{':
            left_d += 1
        elif character == '√{':
            left_r += 1
        elif character == '^√{':
            left_ru += 1
        elif character == '^}':
            right_u += 1
        elif character == '_}':
            right_d += 1
        elif character == '√}':
            right_r += 1
        elif character == '^√}':
            right_ru += 1
        elif character == 'frac}':
            right_f += 1
        elif character == 'frac{':
            left_f += 1
        elif character in all_matrix_left:
            left_m +=1
        elif character in all_matrix_right:
            right_m +=1

        if left_u - right_u >= 1:
            return False
        elif left_d - right_d >= 1:
            return False
        elif left_r - right_r >= 1:
            return False
        elif left_ru - right_ru >= 1:
            return False
        elif left_f - right_f >= 1:
            return False
        return True
    # 文字输入
    def character_input(self, character):
        if sliding:return
        if not self.adding:self.clear_answer()

        if self.result != [[], [], [], []]:
            history.append(deepcopy(self.result))
        '''
        # 尾部追加优化
        if self.adding and self.place == len(self.result[0]):
            if self.__allowed_enter(character):
                s = [0]
            else:
                s = []
            a = self.left_and_right[-1]
        else:
        '''
        s, a = self.get_bplace(I.place)[0], self.get_bplace(I.place)[1]

        if character == r'\\' and not 0 in s:
            self.place +=1
            return
        elif character in ['[', ']', '{', '}']:
            character = '\\'+ character
        self.result[0].insert(self.place, str(character))
        # 数字
        if character in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
            self.result[1].insert(self.place, 23 // (a + 1))
        # 英文小写字母
        elif character in all_el_letters[0]:
            for k in range(len(all_el_letters[0])):
                if all_el_letters[0][k] == character:
                    self.result[1].insert(self.place, all_el_letters[1][k] // (a + 1))
                    break
        # 英文大写字母
        elif character in all_eu_letters[0]:
            for k in range(len(all_eu_letters[0])):
                if all_eu_letters[0][k] == character:
                    self.result[1].insert(self.place, all_eu_letters[1][k] // (a + 1))
                    break
        # 大型运算
        elif character in all_symbols[0] or (character in ['Σ', 'Π', '\\coprod', '∪', '∩', '∨', '∧'] and Bn.choose == 3):
            if a == 0:
                v = {'Σ': '\\sum ', 'Π': '\\prod ', '\\coprod':'\\coprod ', '∪': '\\bigcup ', '∩': '\\bigcap ', '∨': '\\bigvee ', '∧': '\\bigwedge '}
                for k in range(len(all_symbols[0])):
                    if all_symbols[0][k] == character:
                        self.result[1].insert(self.place, all_symbols[1][k])
                        break
                    elif character in v:
                        if all_symbols[0][k] == v[character]:
                            self.result[0][self.place] = v[character]
                            self.result[1].insert(self.place, all_symbols[1][k])
                            break
            else:
                self.result[0].pop(self.place)
        # 希腊小写字母
        elif character in all_gl_letters[0]:
            for k in range(len(all_gl_letters[0])):
                if all_gl_letters[0][k] == character:
                    self.result[1].insert(self.place, all_gl_letters[1][k] // (a + 1))
                    break
        # 希腊大写字母
        elif character in all_gu_letters[0]:
            for k in range(len(all_gu_letters[0])):
                if all_gu_letters[0][k] == character:
                    self.result[1].insert(self.place, all_gu_letters[1][k] // (a + 1))
                    break
        # 关系符 不等式变化
        elif character in all_relations[0]:
            v = {'<': r'\le ', '>': r'\ge ', '∽': '≌', '\\subset ': '\\subseteq ',
                 '\\supset ': '\\supseteq ', '\\sqsubset ': '\\sqsubseteq ', '\\sqsupset ': '\\sqsupseteq '}
            if self.place != 0 and self.result[0][self.place] == '=' and self.result[0][self.place - 1] in v:
                b = self.result[0][self.place - 1]
                self.result[0].pop(self.place)
                self.backspace()
                self.character_input(v[b])
                self.cursor_change(self.place)
                return
            for k in range(len(all_relations[0])):
                if all_relations[0][k] == character:
                    self.result[1].insert(self.place, all_relations[1][k] // (a + 1))
                    break
        # 运算符
        elif character in all_operators[0]:
            for k in range(len(all_operators[0])):
                if all_operators[0][k] == character:
                    self.result[1].insert(self.place, all_operators[1][k] // (a + 1))
                    break
        # 括号
        elif character in all_brackets[0]:
            for k in range(len(all_brackets[0])):
                if all_brackets[0][k] == character:
                    self.result[1].insert(self.place, all_brackets[1][k] // (a + 1))
                    break
        # 上标,下标,分数
        elif character in ['^{', '_{', '^√{', '^}', '_}', '^√}', '√}', '/', r'\\']:
            self.result[1].insert(self.place, 0)
        elif character in ['frac{', 'frac}']:
            self.result[1].insert(self.place, 8 // (a + 1))
        elif character == '√{':
            self.result[1].insert(self.place, 38 // (a + 1))
        # 度分秒
        elif character == '°':
            self.result[1].insert(self.place, 18 // (a + 1))
        elif character in all_points[0]:
            if self.place != 0 and self.result[0][self.place] == '′':
                if self.result[0][self.place - 1] == '′':
                    self.result[0].pop(self.place)
                    self.backspace()
                    self.character_input('″')
                    self.cursor_change(self.place)
                    return
            for k in range(len(all_points[0])):
                if all_points[0][k] == character:
                    self.result[1].insert(self.place, all_points[1][k] // (a + 1))
                    break


        elif character in all_arrows[0]:
            for k in range(len(all_arrows[0])):
                if all_arrows[0][k] == character:
                    self.result[1].insert(self.place, all_arrows[1][k] // (a + 1))
                    break
        # 特殊函数
        elif character in all_special_fuc[0]:
            for k in range(len(all_special_fuc[0])):
                if all_special_fuc[0][k] == character:
                    self.result[1].insert(self.place, all_special_fuc[1][k] // (a + 1))
                    break
        elif character in all_special_fuc2[0]:
            for k in range(len(all_special_fuc2[0])):
                if all_special_fuc2[0][k] == character:
                    self.result[1].insert(self.place, all_special_fuc2[1][k] // (a + 1))
                    break
        # 其它符号
        elif character in all_others[0]:
            for k in range(len(all_others[0])):
                if all_others[0][k] == character:
                    self.result[1].insert(self.place, all_others[1][k] // (a + 1))
                    break
        # 矩阵
        elif character in all_matrix[0]:
            for k in range(len(all_matrix[0])):
                if all_matrix[0][k] == character:
                    self.result[1].insert(self.place, all_matrix[1][k])
                    break
        # 文字
        elif character == '[ERROR]':
            self.result[1].insert(self.place, 325)
        elif character == '[ANSWER]':
            self.result[1].insert(self.place, 63)
        # 其他
        else:
            self.result[1].insert(self.place, 23 // (a + 1))

        if self.adding:
            self.place += 1
        else:
            # 字串移动
            mlong = 0
            while self.px - mlong < 10 and self.start > 0:
                self.start -= 1
                mlong -= 1
            mlong = 0
            while self.px - mlong > size[0] - 40:
                self.start += 1
                mlong += 1

            self.cursor_change(self.place + 1)


    # 回删
    def backspace(self):
        if sliding: return
        self.clear_answer()
        if self.place > 0:
            cdown = False
            if self.result[0][self.place - 1] == '^√{':
                return
            elif self.result[0][self.place - 1] in ['^{', '_{', '√{']:
                for i in range(len(self.result[0][self.place - 1:])):
                    if self.result[0][self.place - 1 + i] == self.result[0][self.place - 1][0] + '}':
                        self.result[0].pop(self.place - 1 + i)
                        self.result[1].pop(self.place - 1 + i)
                        cdown = True
                        if self.result[0][self.place - 1] == '√{':
                            for h in self.result[0][:self.place][::-1]:
                                self.result[0].pop(self.place - 1)
                                self.result[1].pop(self.place - 1)
                                self.cursor_change(self.place - 1)
                                if h == '^√{':
                                    return
                        break
            elif self.result[0][self.place - 1] == 'frac}':
                f = 0
                for h in self.result[0][:self.place][::-1]:
                    if h == 'frac}':
                        f += 1
                    self.result[0].pop(self.place - 1)
                    self.result[1].pop(self.place - 1)
                    self.cursor_change(self.place - 1)
                    if h == 'frac{':
                        f -= 1
                        if f == 0:
                            return
            elif self.result[0][self.place - 1] in ['^}', '_}', '^√}', '√}', 'frac{', '/']:
                self.cursor_change(self.place - 1)
                return
            elif self.result[0][self.place - 1] in all_matrix_left:
                for k in range(len(all_matrix_left)):
                    if all_matrix_left[k] == self.result[0][self.place - 1]:
                        f = 0
                        while True:
                            if self.result[0][self.place - 1] == all_matrix_left[k]:
                                f += 1
                            self.result[0].pop(self.place - 1)
                            self.result[1].pop(self.place - 1)

                            if self.result[0][self.place - 1] == all_matrix_right[k]:
                                f -= 1
                                if f == 0:
                                    break
                        break
            elif self.result[0][self.place - 1] in all_matrix_right:
                for k in range(len(all_matrix_right)):
                    if all_matrix_right[k] == self.result[0][self.place - 1]:
                        f = 0
                        for h in self.result[0][:self.place][::-1]:
                            if h == all_matrix_right[k]:
                                f += 1
                            self.result[0].pop(self.place - 1)
                            self.result[1].pop(self.place - 1)
                            self.cursor_change(self.place - 1)
                            if h == all_matrix_left[k]:
                                f -= 1
                                if f == 0:
                                    return
                        break
            self.result[0].pop(self.place - 1)


            if self.px - self.result[1][self.place - 1] <= 0 and self.start > 0:
                self.start -= size[0] - 10
                if self.start < 0:self.start = 0
            if self.py - self.result[3][self.place - 1] <= 0 and self.top > 0:
                self.top -= 100 + add_height
                if self.top < 0:self.top = 0
            self.result[1].pop(self.place - 1)

            self.cursor_change(self.place - 1)
            if cdown:
                res = self.result[0]
                pla = self.place
                self.__init__()
                for f in res:
                    self.character_input(f)
                self.cursor_change(pla)

    # 光标移动
    def cursor_change(self, place):
        change_screen()
        self.place = place
        self.cursor_show = True
        if self.place > len(self.result[0]):
            self.place = len(self.result[0])
        elif self.place < 0:
            self.place = 0

        # 光标显示位置,长度
        if len(self.result[0]) == 0:
            self.px = 5
            self.py = self.ENDYPLACE
            self.long = 48
        elif self.place == len(self.result[0]):
            self.px = self.coordinate[0][-1] + self.result[1][-1]
            self.py = self.ENDYPLACE

            #self.py = self.coordinate[1][0]
            self.long = 48
        else:
            a = self.result[2][self.place-1]
            self.px = self.coordinate[0][self.place]
            self.py = self.coordinate[1][self.place]
            self.long = 24 * (2 / (a + 1)) - a * 2

    # 光标显示与闪动
    def cursor(self):
        while self.running:
            if pygame.mouse.get_focused():
                self.cursor_show = True
                time.sleep(0.4)
                self.cursor_show = False
                time.sleep(0.4)

    def clear_answer(self):
        if self.clear and "[ANSWER]" in self.result[0]:
            # 清空计算内容
            cut = len(self.result[0])
            for i in range(len(self.result[0])):
                if self.result[0][i] == '[ANSWER]':
                    cut = i-1
                    break
            self.result[0] = self.result[0][:cut]
            self.result[1] = self.result[1][:cut]
            self.result[3] = self.result[3][:cut]
            self.cursor_change(self.place)


#按钮
class Button():
    def __init__(self):
        # 按钮颜色
        self.button_color = (150, 220, 230)
        self.button_mouseon_color = (100, 200, 220)
        self.button_clicked_color = (50, 180, 200)
        self.cbutton_color = (255, 170, 130)
        self.cbutton_mouseon_color = (255, 140, 90)
        self.cbutton_clicked_color = (255, 110, 40)
        # 鼠标状态
        self.mouse_down = False
        self.mouse_on = False
        # 按钮大小
        self.bw = 48
        self.bh = int(self.bw / 3 * 2)
        self.cbw = int((self.bw + 5) * 12 / 8)
        # 被键位置
        self.click_place = [-1, -1]
        # 选择框位置(默认位置)
        self.choose = 1
        # 初始化选择框
        keyboard[2] = keyboardchange[self.choose][0] + keyboard[2][7:]
        keyboard[3] = keyboardchange[self.choose][1] + keyboard[3][7:]
        keyboard[4] = keyboardchange[self.choose][2] + keyboard[4][7:]
        keyboard[5] = keyboardchange[self.choose][3] + keyboard[5][7:]

    def show(self):
        global capslock
        kebord_yplace = 230 + add_height
        for j in range(6):
            # 按钮第一行
            if j == 0:
                for i in range(8):
                    if self.mouse_on and [i, j] == self.click_place:
                        self.cbutton_color = self.cbutton_mouseon_color
                        # 按下鼠标
                        if self.mouse_down:
                            self.cbutton_color = self.cbutton_clicked_color
                        else:
                            self.cbutton_color = self.cbutton_mouseon_color
                    else:
                        self.cbutton_color = (255, 170, 130)
                    if capslock:
                        pygame.draw.rect(screen, (255, 0, 0),
                                         (5 + 5 * (self.cbw + 5), kebord_yplace, self.cbw, self.bh), 3)
                    # 按钮颜色与文字
                    pygame.draw.rect(screen, self.cbutton_color,
                                     (5 + i * (self.cbw + 5), kebord_yplace, self.cbw, self.bh), 0)
                    screen.blit(f.render(keyboard[0][i], 1, (0, 0, 0)), (5 + i * (self.cbw + 5), kebord_yplace + 5))
                continue

            # 其他行
            for i in range(13):
                if self.mouse_on and [i, j] == self.click_place:
                    self.button_color = self.button_mouseon_color
                    # 按下按钮
                    if self.mouse_down:
                        self.button_color = self.button_clicked_color
                    else:
                        self.button_color = self.button_mouseon_color
                else:
                    self.button_color = (150, 220, 230)
                # 按钮颜色
                pygame.draw.rect(screen, self.button_color,
                                 (5 + i * (self.bw + 5), kebord_yplace + j * (self.bh + 5), self.bw, self.bh), 0)
                correction = 0
                if keyboard[j][i] != '':
                    if keyboard[j][i][0] == '\\':
                        # 图片
                        correction = 0
                        im = [
                            ['\\coprod', '\\gg', '\\ni', '\\dashv', '\\subset', '\\supset', '\\sqsubset', '\\sqsupset'],
                            [18, 18, 20, 20, 19, 19, 19, 19]]
                        for k in range(len(im[0])):
                            if keyboard[j][i] == im[0][k]:
                                if k == 4 or k == 5:
                                    add = 6
                                else:
                                    add = 0
                                screen.blit(button_image1,
                                            (i * (self.bw + 3) + 20 + add, kebord_yplace + j * (self.bh + 5) + 5),
                                            (correction, 4, im[1][k], 30))
                                break
                            correction += im[1][k]
                        continue
                        # pass
                # 变化框
                if 0 <= i <= 6 and 2 <= j <= 5:
                    # 不同的选择框
                    # 三角函数
                    if self.choose == 0:
                        if i < 6:
                            screen.blit(f2.render('-1', 1, (0, 0, 0)),
                                        (5 + i * (self.bw + 5) + 23, kebord_yplace + 3 * (self.bh + 5) + 1))
                            screen.blit(f2.render('-1', 1, (0, 0, 0)),
                                        (5 + i * (self.bw + 5) + 31, kebord_yplace + 5 * (self.bh + 5) + 1))
                        screen.blit(f1.render(keyboard[j][i], 1, (0, 0, 0)),
                                    (5 + i * (self.bw + 5), kebord_yplace + j * (self.bh + 5) + 5))
                    # 英文字母
                    elif self.choose == 1:
                        if len(keyboard[j][i]) != 2:
                            screen.blit(f.render(keyboard[j][i], 1, (0, 0, 0)),
                                        (5 + i * (self.bw + 5), kebord_yplace + j * (self.bh + 5) + 5))
                        elif capslock:
                            screen.blit(f.render('  ' + keyboard[j][i][0], 1, (0, 0, 0)),
                                        (5 + i * (self.bw + 5), kebord_yplace + j * (self.bh + 5) + 5))
                        else:
                            screen.blit(f.render('  ' + keyboard[j][i][1], 1, (0, 0, 0)),
                                        (5 + i * (self.bw + 5), kebord_yplace + j * (self.bh + 5) + 5))
                    # 希腊字母
                    elif self.choose == 2:
                        if len(keyboard[j][i]) != 2:
                            screen.blit(f.render(keyboard[j][i], 1, (0, 0, 0)),
                                        (5 + i * (self.bw + 5), kebord_yplace + j * (self.bh + 5) + 5))
                        elif capslock:
                            screen.blit(f.render(' ' + keyboard[j][i][0], 1, (0, 0, 0)),
                                        (5 + i * (self.bw + 5), kebord_yplace + j * (self.bh + 5) + 5))
                        else:
                            screen.blit(f.render(' ' + keyboard[j][i][1], 1, (0, 0, 0)),
                                        (5 + i * (self.bw + 5), kebord_yplace + j * (self.bh + 5) + 5))
                    else:
                        screen.blit(f.render(keyboard[j][i], 1, (0, 0, 0)),
                                    (5 + i * (self.bw + 5), kebord_yplace + j * (self.bh + 5) + 5))

                else:
                    screen.blit(f.render(keyboard[j][i], 1, (0, 0, 0)),
                                (5 + i * (self.bw + 5), kebord_yplace + j * (self.bh + 5) + 5))
                screen.blit(button_image, (10 + 8 * (self.bw + 3) + 20, kebord_yplace + 2 * (self.bh + 5) + 5),
                            (0, 5, 27, 50))
                screen.blit(button_image, (10 + 8 * (self.bw + 5) + 10, kebord_yplace + 3 * (self.bh + 5) + 1),
                            (26, 0, 20, 50))
                screen.blit(button_image, (10 + 8 * (self.bw + 5) + 5, kebord_yplace + 4 * (self.bh + 5) + 1),
                            (44, 0, 28, 50))
                screen.blit(button_image, (10 + 7 * (self.bw + 5) + 5, kebord_yplace + 4 * (self.bh + 5) + 1),
                            (72, 0, 28, 50))

        # 选择框(红框)
        pygame.draw.rect(screen, (255, 0, 0), (5 + self.choose * (self.cbw + 5), kebord_yplace, self.cbw, self.bh), 3)
        # 变化框(黑框)
        pygame.draw.rect(screen, (0, 0, 0),
                         (2, kebord_yplace + 2 * (self.bh + 5) - 3, 7 * (self.bw + 5), 4 * (self.bh + 5)), 2)

    # 获取按键位置
    def mouse(self, x, y):
        cy = (y - (228 + add_height + 5 + self.bh)) // (self.bh + 5) + 1
        if cy == 0:
            cx = (x - 5) // (self.cbw + 5)
        else:
            cx = (x - 5) // (self.bw + 5)
        self.click_place = [cx, cy]

    # 点击按键
    def click(self, place):
        global capslock, memory

        if place[1] >= len(keyboard):
            return
        if place[0] >= len(keyboard[place[1]]):
            return
        button_txt = keyboard[place[1]][place[0]].replace(' ', '')
        # 选择类别
        if place[1] == 0 and 0 <= place[0] <= 4:
            self.choose = place[0]
            keyboard[2] = keyboardchange[self.choose][0] + keyboard[2][7:]
            keyboard[3] = keyboardchange[self.choose][1] + keyboard[3][7:]
            keyboard[4] = keyboardchange[self.choose][2] + keyboard[4][7:]
            keyboard[5] = keyboardchange[self.choose][3] + keyboard[5][7:]

        elif button_txt != '':
            I.adding = True
            # 其他表示字符
            if button_txt[0] == "\\":
                I.character_input(button_txt)
            # 特殊表示字符
            elif button_txt == '|≡|':
                I.character_input(r'\begin{vmatrix}')
                I.character_input(r'\end{vmatrix}')
                I.cursor_change(I.place - 1)
            elif button_txt == '(≡)':
                I.character_input(r'\begin{pmatrix}')
                I.character_input(r'\end{pmatrix}')
                I.cursor_change(I.place - 1)
            elif button_txt == '[≡]':
                I.character_input(r'\begin{bmatrix}')
                I.character_input(r'\end{bmatrix}')
                I.cursor_change(I.place - 1)
            elif button_txt == '{≡}':
                I.character_input(r'\begin{Bmatrix}')
                I.character_input(r'\end{Bmatrix}')
                I.cursor_change(I.place - 1)
            elif button_txt == '[+]':
                I.character_input(r'&')

            # 选择框按钮事件
            elif place == [5, 0]:
                capslock = not capslock
            elif place == [6, 0]:
                if len(history) != 1:
                    history.pop(-1)
                I.result = history[-1]
                I.cursor_change(len(history[-1][1]))
            elif place == [7, 0]:
                self.calculate()
            elif place == [0, 1]:
                memory = []
            elif place == [1, 1]:
                if memory != []:
                    I.result[0] = I.result[0][:I.place] + memory[-1][0] + I.result[0][I.place:]
                    I.result[1] = I.result[1][:I.place] + memory[-1][1] + I.result[1][I.place:]
                    I.result[2] = I.result[2][:I.place] + memory[-1][2] + I.result[2][I.place:]
                    I.result[3] = I.result[3][:I.place] + memory[-1][3] + I.result[3][I.place:]
                    change_screen()
            elif place == [2, 1]:
                if '[ANSWER]' in I.result[0]:
                    for k, ca in enumerate(I.result[0]):
                        if ca == '[ANSWER]':
                            memory.append([])
                            memory[-1].append(deepcopy(I.result[0][k+1:]))
                            memory[-1].append(deepcopy(I.result[1][k+1:]))
                            memory[-1].append(deepcopy(I.result[2][k+1:]))
                            memory[-1].append(deepcopy(I.result[3][k+1:]))
                else:
                    memory.append(deepcopy(I.result))
            elif place == [3, 1]:
                I.character_input(r'\begin{cases}')
                I.character_input(r'\end{cases}')
                I.cursor_change(I.place - 1)
            elif place == [4, 1]:
                I.character_input(r'\\')
                sliding = True
                mlong = 0
                while I.px - mlong < 10 and I.start > 0:
                    I.start -= 1
                    mlong -= 1
                mlong = 0
                while I.py - mlong > 223 + add_height - 100:
                    I.top += 1
                    mlong += 1
                sliding = False
                I.cursor_change(I.place)
            elif place == [12, 1]:
                I.backspace()
            elif place == [11, 1]:
                I.__init__()
            elif place == [7, 1]:#左
                I.cursor_change(I.place - 1)
                mlong = 0
                while I.px - mlong < 10 and I.start > 0:
                    I.start -= 1
                    mlong -= 1
                mlong = 0
                while I.px - mlong > size[0] - 10:
                    I.start += 1
                    mlong += 1
                if I.result[0][I.place - 1] == '^√}':
                    I.cursor_change(I.place - 1)
            elif place == [8, 1]:#上
                standard = Inf
                temp = I.place - 1
                for h in range(len(I.coordinate[1])):
                    if I.coordinate[1][h] >= I.coordinate[1][I.place - 1]: continue

                    distance = abs(I.coordinate[1][I.place - 1] - I.coordinate[1][h]) + abs(
                        I.coordinate[0][I.place - 1] - I.coordinate[0][h])
                    if distance < standard:
                        temp = h
                        standard = distance
                mlong = 0
                while I.py - mlong < 50 and I.top > 0:
                    I.top -= 1
                    mlong -= 1
                if I.result[0][temp] == '^√}':
                    I.cursor_change(temp)
                else:
                    I.cursor_change(temp + 1)
            elif place == [9, 1]:#下
                standard = Inf
                temp = I.place - 1
                for h in range(len(I.coordinate[1])):
                    if I.coordinate[1][h] <= I.coordinate[1][I.place - 1]: continue

                    distance = abs(I.coordinate[1][I.place - 1] - I.coordinate[1][h]) + abs(
                        I.coordinate[0][I.place - 1] - I.coordinate[0][h])
                    if distance < standard:
                        temp = h
                        standard = distance

                mlong = 0
                while I.py - mlong > 223 + add_height - 100:
                    I.top += 1
                    mlong += 1
                if I.result[0][temp] == '^√}':
                    I.cursor_change(temp)
                else:
                    I.cursor_change(temp + 1)
            elif place == [10, 1]:#右
                I.cursor_change(I.place + 1)
                mlong = 0
                while I.px - mlong < 10 and I.start > 0:
                    I.start -= 1
                    mlong -= 1
                mlong = 0
                while I.px - mlong > size[0] - 10:
                    I.start += 1
                    mlong += 1
                if I.result[0][I.place - 1] == '^√}':
                    I.cursor_change(I.place + 1)
            elif place == [8, 2]:
                I.character_input('^√{')
                I.character_input('^√}')
                I.character_input('√{')
                I.character_input('√}')
                I.cursor_change(I.place - 1)
            elif place == [8, 3]:
                I.character_input('frac{')
                I.character_input('/')
                I.character_input('frac}')
                I.cursor_change(I.place - 2)
            elif place == [8, 4]:
                I.character_input('^{')
                I.character_input('^}')
                I.cursor_change(I.place - 1)
            elif place == [7, 4]:
                I.character_input('_{')
                I.character_input('_}')
                I.cursor_change(I.place - 1)
            elif 0 <= place[0] <= 6 and 2 <= place[1] <= 5:
                if self.choose == 0 or self.choose == 3:
                    if len(button_txt) > 1:
                        newtxt = button_txt.replace('(', '')
                        I.character_input(newtxt)
                        if (place[1] == 3 or place[1] == 5) and self.choose == 0:
                            I.character_input('^{')
                            I.character_input('-')
                            I.character_input(1)
                            I.character_input('^}')
                        #I.character_input('(')

                    else:
                        I.character_input(button_txt)
                elif (self.choose == 1 or self.choose == 2) and len(button_txt) == 2:
                    if capslock:
                        I.character_input(button_txt[0])
                    else:
                        I.character_input(button_txt[1])
                else:
                    I.character_input(button_txt.replace('(', ''))
            elif len(button_txt) > 1:
                newtxt = button_txt.replace('(', '')
                I.character_input(newtxt)
            elif place != [-1, -1]:
                I.character_input(button_txt)
            I.adding = False

    # 计算
    def calculate(self):
        I.clear_answer()
        I.clear = False
        I.adding = True

        miplace = I.place
        I.cursor_change(len(I.result[0]))

        # 输出显示结果
        if I.result[0] != []:
            answer = calculation(I.result[0])
            I.character_input(r'\\')
            I.character_input('[ANSWER]')
            #print("写入内容")
            if answer[0] == r'\text':
                TEXT = '[ERROR]'
                for k in answer[1:]:TEXT += k
                I.character_input(TEXT)
            else:
                for i in answer:
                    I.character_input(i)
        #print("完成")
        I.cursor_change(miplace)
        I.clear = True
        I.adding = False

        print('输入(列表):'+str(I.result[0]))
        print('字符长度:'+str(I.result[1]))
        print('尺寸类型:'+str(I.result[2]))
        print('字符高度:'+str(I.result[3]))
        print('字符横坐标:' + str(I.coordinate[0]))
        print('字符纵坐标:' + str(I.coordinate[1]))
        #1:输入(列表),2:字符长度,3:分数层级,4:字符高度,5:光标所在位置字符位置


# 刷新
def change_screen():
    global add_height
    add_height = size[1] - 460
    screen.fill((255, 255, 255))
    # screen.fill((150,150,150))
    # I.result[2] = Frac.frac_new(I.result[0])
    I.show()
    pygame.draw.rect(screen, (255, 255, 255), (0, 0, size[0], 21), 0)
    pygame.draw.rect(screen, (255, 255, 255), (0, 220 + add_height, size[0], 300), 0)
    #pygame.draw.rect(screen, (0, 0, 0), (0, 21, size[0], 198 + add_height), 5)
    pygame.draw.rect(screen, (0, 0, 0), (0, 21, size[0], 3), 0)
    pygame.draw.rect(screen, (0, 0, 0), (0, 219 + add_height, size[0], 3), 0)
# 复制
def copylatex():
    express = ''.join(I.result[0])
    express = express.replace('[ANSWER]', 'Answer:')
    express = express.replace('[ERROR]', 'Error')
    latexexpress = transform(inputexpress=express)
    # 向剪切板写入文本
    pyperclip.copy(latexexpress)
# 粘贴
def pastelatex():
    text = pyperclip.paste()
    input_text = transform(latexexpress=text)
    I.adding = True
    for i in input_text:
        I.character_input(i)
    I.adding = False

add_height = size[1] - 460
downplace = None,None
sliding = False

I = Input_box()
Bn = Button()
threading.Thread(target=I.cursor).start()

change_screen()

# 程序主循环
while True:
    # 操作检测
    x = pygame.mouse.get_pos()[0]
    y = pygame.mouse.get_pos()[1]
    add_height = size[1] - 460
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            I.running = False
            pygame.quit()
            sys.exit()

        elif event.type == VIDEORESIZE:
            size = event.size
            if size[0] < int((Bn.bw + 5) * 13) + 5:
                size = int((Bn.bw + 5) * 13) + 5, size[1]
            if size[1] < 400:
                size = size[0], 400
            screen = pygame.display.set_mode(size, RESIZABLE, 32)
            change_screen()

        # 鼠标操作
        elif event.type == MOUSEBUTTONDOWN:
            Bn.mouse_down = True
            # 屏幕内移动光标
            # 复制
            if 10 < x < 110 and 0 < y <= 20:
                copylatex()
            elif 120 < x < 220 and 0 < y <= 20:
                pastelatex()
            # 更多信息
            elif 230 < x < 300 and 0 < y <= 20:
                import webbrowser
                webbrowser.open("https://www.github.com")
            # 主窗口
            elif 1 < x < size[0] - 5 and 20 < y < 223 + add_height:
                ipl = 0
                downplace = x,y
                sliding = True
                downxstart = I.start
                downystart = I.top
                Bn.mouse_on = False
                # 点击光标位置
                cplace = 0
                for i in range(len(I.coordinate[0])):
                    if abs(I.coordinate[0][i]+I.result[1][i]//2-x)+abs(I.coordinate[1][i]+I.result[3][i]//2-y) < \
                            abs(I.coordinate[0][cplace]+I.result[1][cplace]//2-x)+abs(I.coordinate[1][cplace]+I.result[3][cplace]//2-y):
                        cplace = i
                if len(I.coordinate[0]) !=0:
                    if abs(I.coordinate[0][-1]+I.result[1][-1]-x)+abs(I.coordinate[1][-1]+I.result[3][i]//2-y)< \
                            abs(I.coordinate[0][cplace]+I.result[1][cplace]//2-x)+abs(I.coordinate[1][cplace]+I.result[3][cplace]//2-y):
                        cplace = len(I.coordinate[0])
                if (I.result[0][cplace+1] == "^√}"):cplace-=1;
                I.cursor_change(cplace)

            Bn.click(Bn.click_place)
            #change_screen()

        if event.type == MOUSEBUTTONUP:
            Bn.mouse_down = False
            downplace = None,None
            sliding = False
            I.cursor_change(I.place)

        elif event.type == MOUSEMOTION:
            if sliding and downplace[0] != None:
                I.start = downxstart -(x - downplace[0])
                I.top = downystart -(y - downplace[1])
                change_screen()

        # 按键操作
        elif event.type == KEYDOWN:
            #print (event.key)
            if event.key == K_CAPSLOCK:
                capslock = not capslock
            elif event.key == K_LSHIFT or event.key == K_RSHIFT:
                capslock = True

            elif 1073741912 < event.key <= 1073741922:
                m = event.key - 1073741912
                if m == 10: m = 0
                I.character_input(m)
            elif event.key == K_BACKSPACE:
                I.backspace()
            elif event.key == K_SPACE:
                I.character_input(r'&')
            # 左
            elif event.key == K_LEFT:
                sliding = True
                I.cursor_change(I.place - 1)
                mlong = 0
                while I.px - mlong < 10 and I.start > 0:
                    I.start -= 1
                    mlong -= 1
                mlong = 0
                while I.px - mlong > size[0] - 10:
                    I.start += 1
                    mlong += 1
                if I.place - 1 >=0 and len(I.result[0]) > 0:
                    if I.result[0][I.place - 1] == '^√}':
                        I.cursor_change(I.place - 1)
                sliding = False
                I.cursor_change(I.place)
            # 右
            elif event.key == K_RIGHT:
                sliding = True
                I.cursor_change(I.place + 1)
                mlong = 0
                while I.px - mlong < 10 and I.start > 0:
                    I.start -= 1
                    mlong -= 1
                mlong = 0
                while I.px - mlong > size[0] - 10:
                    I.start += 1
                    mlong += 1
                if I.place - 1 >=0 and len(I.result[0]) > 0:
                    if I.result[0][I.place - 1] == '^√}':
                        I.cursor_change(I.place + 1)
                sliding = False
                I.cursor_change(I.place)
            # 上
            elif event.key == K_UP:
                standard = Inf
                temp = I.place-1
                for h in range(len(I.coordinate[1])):
                    if I.coordinate[1][h] >= I.coordinate[1][I.place-1]:continue

                    distance = abs(I.coordinate[1][I.place - 1] - I.coordinate[1][h]) + abs(
                        I.coordinate[0][I.place - 1] - I.coordinate[0][h])
                    if distance < standard:
                        temp = h
                        standard = distance
                mlong = 0
                while I.py - mlong < 50 and I.top > 0:
                    I.top -= 1
                    mlong -= 1
                if I.result[0] == []:break
                if I.result[0][temp] == '^√}':
                    I.cursor_change(temp)
                else:
                    I.cursor_change(temp + 1)
            # 下
            elif event.key == K_DOWN:
                standard = Inf
                temp = I.place - 1
                for h in range(len(I.coordinate[1])):
                    if I.coordinate[1][h] <= I.coordinate[1][I.place - 1]: continue

                    distance = abs(I.coordinate[1][I.place - 1] - I.coordinate[1][h]) + abs(
                        I.coordinate[0][I.place - 1] - I.coordinate[0][h])
                    if distance < standard:
                        temp = h
                        standard = distance
                mlong = 0
                while I.py - mlong > 223 + add_height - 100:
                    I.top +=1
                    mlong +=1
                if I.result[0] == []: break
                if I.result[0][temp] == '^√}':
                    I.cursor_change(temp)
                else:
                    I.cursor_change(temp + 1)
            # 按F11切换全屏,或窗口
            elif event.key == K_F11:
                fullscreen = not fullscreen
                if fullscreen:
                    # 全屏效果，参数重设
                    size = pygame.display.list_modes()[0]
                    screen = pygame.display.set_mode(size, pygame.FULLSCREEN | pygame.HWSURFACE)

                else:
                    size = 700, 500
                    screen = pygame.display.set_mode(size, RESIZABLE, 32)
            elif event.key == K_RETURN or event.key == K_KP_ENTER:
                I.character_input(r'\\')
                sliding = True
                mlong = 0
                while I.px - mlong < 10 and I.start > 0:
                    I.start -= 1
                    mlong -= 1
                mlong = 0
                while I.py - mlong > 223 + add_height - 100:
                    I.top += 1
                    mlong += 1
                sliding = False
                I.cursor_change(I.place)


            elif event.key == pygame.K_c and (event.mod & pygame.KMOD_CTRL):
                copylatex()
            elif event.key == pygame.K_v and (event.mod & pygame.KMOD_CTRL):
                pastelatex()

            # 键盘输入
            # 大写锁定或shift长按
            if not (event.mod & pygame.KMOD_CTRL):

                if capslock:
                    if event.key in eu_letters:
                        I.character_input(eu_letters[event.key])
                    elif event.key == K_EQUALS:
                        I.character_input('+')
                    elif event.key in relations:
                        I.character_input(relations[event.key])
                    elif event.key == 57:
                        I.character_input('(')
                    elif event.key == 48:
                        I.character_input(')')
                    elif event.key == K_SEMICOLON:
                        I.character_input(":")
                    elif event.key == K_BACKSLASH:
                        I.character_input("|")
                    elif event.key == K_LEFTBRACKET:
                        I.character_input("{")

                    elif event.key == K_RIGHTBRACKET:
                        I.character_input("}")
                    elif event.key == 54:#上标
                        I.adding = True
                        I.character_input('^{')
                        I.character_input('^}')
                        I.adding = False
                        I.cursor_change(I.place - 1)
                    elif event.key == K_MINUS:#下标
                        I.adding = True
                        I.character_input('_{')
                        I.character_input('_}')
                        I.adding = False
                        I.cursor_change(I.place - 1)
                    elif event.key == 47 or event.key == 1073741908:#分数
                        I.character_input('frac{')
                        I.character_input('/')
                        I.character_input('frac}')
                        I.cursor_change(I.place - 2)

                else:
                    if event.key in el_letters:
                        I.character_input(el_letters[event.key])
                    elif event.key in operators:
                        I.character_input(operators[event.key])
                    elif event.key in brackets:
                        I.character_input(brackets[event.key])
                    elif 48 <= event.key <= 57:
                        m = event.key - 48
                        I.character_input(m)
                    elif event.key == K_EQUALS:
                        I.character_input('=')

        elif event.type == KEYUP:
            if event.key == K_LSHIFT or event.key == K_RSHIFT:
                capslock = False


        if I.start < 0:
            I.start = 0
            change_screen()
        if I.top < 0:
            I.top = 0
            change_screen()


    if I.cursor_show and not sliding:
        pygame.draw.rect(screen, (0, 0, 0), (I.px, I.py, 2, I.long), 0)
    else:
        pygame.draw.rect(screen, (255, 255, 255), (I.px, I.py, 2, I.long), 0)

    # 按键行为
    if 5 < x < int((Bn.bw + 5) * 13) and 228 + add_height < y < 223 + add_height + (Bn.bh + 5) * 6:
        Bn.mouse(x, y)
        Bn.mouse_on = True
    else:
        Bn.click_place = [-1, -1]
        Bn.mouse_on = False
    Bn.show()
    '''
    #显示鼠标位置(测试用)
    pygame.draw.rect(screen, (255, 255, 255), (0, 0, 800, 20), 0)# 更新
    screen.blit(f1.render(f'x:{x} y:{y}', 1, (0, 0, 0)), (0, 0))
    screen.blit(f1.render(f'I.place: {I.place}', 1, (0, 0, 0)), (100, 0))
    screen.blit(f1.render(f'I.px: {I.px} I.py: {I.py} I.top: {I.top} I.start:{I.start}', 1, (0, 0, 0)), (200, 0))
    '''
    pygame.draw.rect(screen, (255, 255, 255), (0, 0, 500, 20), 0)# 更新

    screen.blit(f1.render('复制LaTex格式', 1, (0, 0, 0)), (10, 2))
    screen.blit(f1.render('粘贴LaTex格式', 1, (0, 0, 0)), (120, 2))
    screen.blit(f1.render('更多信息', 1, (0, 0, 0)), (230, 2))
    
    if 10 < x < 110 and 0 < y <= 20:
        screen.blit(f1.render('复制LaTex格式', 1, (0, 0, 255)), (10, 2))
    elif 120 < x < 220 and 0 < y <= 20:
        screen.blit(f1.render('粘贴LaTex格式', 1, (0, 0, 255)), (120, 2))
    elif 230 < x < 300 and 0 < y <= 20:
        screen.blit(f1.render('更多信息', 1, (0, 0, 255)), (230, 2))

    # 更新图像
    pygame.display.flip()
