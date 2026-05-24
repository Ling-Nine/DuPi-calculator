import pygame

from pygame.locals import *

size = 700,460


logo = pygame.image.load("./符号图片/度派(小).jpg")


icon = pygame.image.load("./符号图片/pi.jpg")
pygame.display.set_icon(icon)

screen = pygame.display.set_mode(size, pygame.RESIZABLE)
pygame.display.set_caption('度派计算器')

screen.fill((255, 255, 255))
pygame.draw.rect(screen, (0, 0, 0), (0, 0, size[0] ,2), 0)
screen.blit(logo, (size[0]//2-110, size[1]//2-100),(0,0,204,206))

pygame.init()

pygame.display.flip()
#数字显示
f_number = [pygame.font.Font('./字体/NewCM10-Book.otf',46),
            pygame.font.Font('./字体/NewCM10-Book.otf',23)]
#字母显示
f_character = [pygame.font.Font('字体/NewCM10-BookItalic.otf', 46),
               pygame.font.Font('字体/NewCM10-BookItalic.otf', 23)]

f_letter = pygame.font.Font('字体/timesi.ttf', 50)
f_character_input = pygame.font.Font('字体/timesi.ttf', 50)

f = pygame.font.Font(r"C:\Windows\Fonts\simsun.ttc",20)
f1 = pygame.font.Font(r"C:\Windows\Fonts\simsun.ttc",15)
f2 = pygame.font.Font(r"C:\Windows\Fonts\simsun.ttc",10)
f4 = pygame.font.Font(r"C:\Windows\Fonts\simsun.ttc",40)

#fnemu = pygame.font.SysFont('simsunnsimsun',12)

image_type = '.png'
nums = pygame.image.load("./符号图片/度数"+image_type)
nums = [pygame.transform.scale(nums, (240, 40)),pygame.transform.scale(nums, (120, 20))]

letters = pygame.image.load("./符号图片/英文字母"+image_type)
letters = [pygame.transform.scale(letters, (642, 60)),pygame.transform.scale(letters, (321, 30))]

uletters = pygame.image.load("./符号图片/大写英文字母"+image_type)
uletters = [pygame.transform.scale(uletters, (864, 60)),pygame.transform.scale(uletters, (432, 30))]

gletters = pygame.image.load("./符号图片/希腊字母"+image_type)
gletters = [pygame.transform.scale(gletters, (636, 60)),pygame.transform.scale(gletters, (318, 30))]

guletters = pygame.image.load("./符号图片/大写希腊字母"+image_type)
guletters = [pygame.transform.scale(guletters, (688, 50)),pygame.transform.scale(guletters, (344, 25))]

operator = pygame.image.load("./符号图片/二元运算符"+image_type)
operator = [pygame.transform.scale(operator, (1086, 60)),pygame.transform.scale(operator, (543, 30))]

bracket = pygame.image.load("./符号图片/括号"+image_type)
bracket = [pygame.transform.scale(bracket, (118, 50)),pygame.transform.scale(bracket, (59, 25))]

relation = pygame.image.load("./符号图片/二元关系符"+image_type)
relation = [pygame.transform.scale(relation, (789, 60)),pygame.transform.scale(relation, (394, 30))]

symbol = pygame.image.load("./符号图片/大型运算"+image_type)
symbol = pygame.transform.scale(symbol, (457, 100))

point = pygame.image.load("./符号图片/点分秒"+image_type)
point = [pygame.transform.scale(point, (133, 40)),pygame.transform.scale(point, (66, 20))]

arrow = pygame.image.load("./符号图片/箭头符号"+image_type)
arrow = [pygame.transform.scale(arrow, (267, 40)),pygame.transform.scale(arrow, (133, 20))]

special_fuc = pygame.image.load("./符号图片/特殊函数"+image_type)
special_fuc = [pygame.transform.scale(special_fuc, (1186, 70)),pygame.transform.scale(special_fuc, (593, 35))]

special_fuc2 = pygame.image.load("./符号图片/特殊函数2"+image_type)
special_fuc2 = [pygame.transform.scale(special_fuc2, (1014, 70)),pygame.transform.scale(special_fuc2, (507, 35))]

others = pygame.image.load("./符号图片/其它符号"+image_type)
others = [pygame.transform.scale(others, (533, 60)),pygame.transform.scale(others, (266, 30))]

button_image = pygame.image.load("./符号图片/符号.jpg")
button_image = pygame.transform.scale(button_image, (96, 30))

button_image1 = pygame.image.load("./符号图片/按键"+image_type)

root = pygame.image.load("./符号图片/根号.jpg")
def root_h(height = 50):
     if height <= 0 or height == float('inf'):height = 20
     return [pygame.transform.scale(root, (100, height)), pygame.transform.scale(root, (50, height))]

matrix = pygame.image.load("./符号图片/矩阵"+image_type)
def matrix_h(height=60):
    if height <= 0 or height == float('inf'): height = 60
    return pygame.transform.scale(matrix, (256, height))

ANSWER = pygame.image.load("./符号图片/结果.png")
ANSWER = pygame.transform.scale(ANSWER, (63, 40))

#默认不全屏
fullscreen = False

#默认小写
capslock = False

el_letters = {
K_a:'a',K_b:'b',K_c:'c',K_d:'d',K_e:'e',K_f:'f',
K_g:'g',K_h:'h',K_i:'i',K_j:'j',K_k:'k',K_l:'l',
K_m:'m',K_n:'n',K_o:'o',K_p:'p',K_q:'q',K_r:'r',
K_s:'s',K_t:'t',K_u:'u',K_v:'v',K_w:'w',K_x:'x',
K_y:'y',K_z:'z'
}
eu_letters = {}
for x in el_letters:
     eu_letters[x] = el_letters[x].upper()

operators = {
K_PLUS:'+',K_MINUS:'-',K_ASTERISK:'×',K_SLASH:'÷',K_PERIOD:'.',
K_KP_PLUS:'+',K_KP_MINUS:'-',K_KP_MULTIPLY:'×',K_KP_DIVIDE:'÷',K_KP_PERIOD:'.'
}
brackets = {
K_LEFTBRACKET:'[',K_RIGHTBRACKET:']'
}
relations = {
K_COMMA:'<',K_PERIOD:'>',K_EQUALS:'='
}

all_operators = [[
'+', '-', '×', '÷', '±', '\\mp ', '\\triangleleft ', '\\triangleright ',
'\\cdot ', '\\setminus ', '\\star ', '\\ast ', '\\cup ' '\\cap ', '\\sqcup ', '\\sqcap ',
'\\vee ', '\\wedge ', '\\circ ', '\\bullet ', '\\oplus ', '\\ominus ', '\\odot ', '\\oslash ',
'\\otimes ', '\\bigcirc ', '\\diamond ', '\\uplus ', '\\bigtriangleup ', '\\bigtriangledown ',
'\\lhd ', '\\rhd ', '\\unlhd ', '\\unrhd ', '\\amalg ', '\\wr ', '\\dagger ', '\\ddagger '],
[32,36,27,25,23,23,25,25,25,25,25,25,25,25,25,25,25,25,25,25,25,25,]
]
all_brackets = [['(',')','|','\\[','\\]','\\{','\\}'],[16,16,10,14,14,22,22]]
all_symbols = [
['\\sum ','∫','∮','\\prod ','\\coprod ','\\bigcup ','\\bigcap ','\\bigvee ','\\bigwedge '],
[55,39,39,57,57,50,50,52,52],[10,20,20,10,10,10,10,10,10]
]
all_relations = [[
'<', '>', '=', '\\le ', '\\ge ', '≡', '∽', '\\gg ', '≈','≌', '∝', '∈', '\\ni ', ':','\\dashv ', '≠',
'\\subset ','\\supset ','\\subseteq ','\\supseteq ','\\sqsubset ','\\sqsupset ','\\sqsubseteq ','\\sqsupseteq ', ','],
[32,32,36,32,32,36,33,33,33,33,35,27,27,16,27,33,33,33,33,33,35,35,32,32,14]
]
all_el_letters = [[el_letters[x] for x in el_letters],[23,23,21,25,23,25,23,27,16,23,23,14,43,28,23,27,22,20,21,18,27,24,34,26,26,23]]
all_eu_letters = [[eu_letters[x] for x in eu_letters],[31,33,31,34,33,31,32,37,22,26,37,29,42,38,31,33,31,33,26,30,32,32,42,36,33,30]]

all_gl_letters = [[
'α','β','γ','δ','ε','ζ','η','θ','ι','κ','λ','μ',
'ν','ξ','ο','π','ρ','σ','τ','υ','φ','χ','ψ','ω'],
[30,28,28,20,20,22,24,23,18,27,28,30,25,23,23,27,25,28,26,25,29,30,32,30]
]

all_points = [['.','′','·','″'],[10,18,22,18]]
all_arrows = [[
'←','→','↑','↓','⇐','⇒','⇑','⇓','\\rightleftharpoons '],
[34,34,17,17,33,33,20,20,35]
]
all_gu_letters = [[
'A','B','Γ','Δ','E','Z','H','Θ','I','K','Λ','M',
'N','Ξ','O','Π','P','Σ','T','Υ','Φ','X','Ψ','Ω'],
[29,26,24,31,28,27,32,27,20,32,26,37,34,23,28,28,29,25,26,29,26,31,28,28]
]

all_special_fuc = [['lim','log','lg','ln','sin','cos','tan','cot','sec','csc','sinh','cosh','tanh','coth','sech','csch'],
                   [70,65,45,45,64,66,73,65,65,65,86,92,95,92,89,89]]
all_special_fuc2 = [['det','arcsin','arccos','arctan','arccot','arcsec','arccsc'],
                    [75,100,100,100,100,100,100,100,100]]

all_others = [['!', '％', '∞', '∂'],[10,40,50,20]]

all_matrix = [[r'\begin{cases}',r'\end{cases}',r'\begin{pmatrix}',r'\end{pmatrix}',
               r'\begin{bmatrix}',r'\end{bmatrix}',r'\begin{vmatrix}',r'\end{vmatrix}',
                r'\begin{Vmatrix}',r'\end{Vmatrix}',r'\begin{Bmatrix}',r'\end{Bmatrix}'],
              [25,20,20,20,20,20,12,12,32,32,26,26]]
all_matrix_left = [r'\begin{cases}',r'\begin{pmatrix}',r'\begin{bmatrix}',r'\begin{vmatrix}',r'\begin{Vmatrix}',r'\begin{Bmatrix}']
all_matrix_right = [r'\end{cases}',r'\end{pmatrix}',r'\end{bmatrix}',r'\end{vmatrix}',r'\end{Vmatrix}',r'\end{Bmatrix}']


#==========================================按键排布============================================
nemu = ['菜单','存储','设置','关于']

keyboard = [
['三角函数','英文字母','希腊字母','计算符号','其它符号','  大写','  撤销','  计算'],
[' MC',' MR',' M+',' {≡','回车','  e',' π',' ←',' ↑',' ↓',' →','清空','退格'],
['','','','','','','','log(','  ·','  7','  8','  9','  +'],
['','','','','','','',' ln(','  .','  4','  5','  6','  -'],
['','','','','','','',' ·',' ·','  1','  2','  3',' ×'],
['','','','','','','','  (','  )','  .','  0','  =',' ÷']
]

memory = []

keyboardchange = [
[[' sin(',' cos(',' tan(',' cot(',' sec(',' csc(','  °'],
 ['sin (','cos (','tan (','cot (','sec (','csc (','  ′'],
 ['sinh(','csoh(','tanh(','coth(','sech(','csch(','  ″'],
 ['sinh (','csoh (','tanh (','coth (','sech (','csch (','  ％']],
[['Aa','Bb','Cc','Dd','Ee','Ff','Gg'],
 ['Hh','Ii','Jj','Kk','Ll','Mm','Nn'],
 ['Oo','Pp','Qq','Rr','Ss','Tt','Uu'],
 ['Vv','Ww','Xx','Yy','Zz','','']],
[['Aα','Bβ','Γγ','Δδ','Eε','Zζ','Hη'],
 ['Θθ','Iι','Kκ','Λλ','Mμ','Nν','Ξξ'],
 ['Oo','Ππ','Pρ','Σσ','Tτ','Υυ','Φφ'],
 ['Xχ','Ψψ','Ωω','','','','']],
[[' lim',' ∫',' ∮',' ∞',' ·',' ≡',' !'],
 [' lg(','  |','  <','  >','  ,',' ±',' ∝'],
 [' ←',' ↑',' ↓',' →',' ∈',' Σ',' ≠'],
 [' Π','\\coprod',' ∪',' ∩',' ∨',' ∧',' ∽']],
[['\\gg','\\ni','\\dashv','\\subset','\\supset','  :',' ≈'],
 ['\\sqsubset','\\sqsupset','  [','  ]','  {','  }',' ≌'],
 ['|≡|','[≡]','(≡)','{≡}',' [+]','det(',''],
 ['','','','','','','']]
]

history = []