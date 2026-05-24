from latex2sympy2 import latex2sympy,latex2latex
from sympy import *
import re
import time
import numpy as np
from scipy.optimize import fsolve, root
import threading
import queue
from sympy import CRootOf, Poly

from sympy.core.relational import Relational

# 全局设置
MAX_SYMBOLIC_TIME = 3  # 符号计算最大时间（秒）
MAX_NUMERIC_TIME = 10  # 数值计算最大时间（秒）

"""主计算函数，处理各种数学表达式"""
def latex_calculator(latex_input):

    try:
        # 确保输入是字符串
        if not isinstance(latex_input, str):
            latex_input = str(latex_input)

        # 预处理：移除多余空格
        latex_input = re.sub(r'\s+', ' ', latex_input.strip())

        # 6. 检测方程（严格验证）
        if is_potential_equation(latex_input):
            return solve_equation(latex_input)

        # 1. 检测特殊结构（级数、积分、极限、矩阵）
        if any(func in latex_input for func in [r'\sum', r'\int', r'\prod', r'\lim']):
            expr = latex2sympy(latex_input)
            result = expr.doit()
            return latex(result)

            #return latex2latex(latex_input)
        # 2. 检测矩阵
        if re.search(r'\\begin\{[a-z]*matrix', latex_input):
            return process_matrix(latex_input)

        # 3. 检测不等式组/方程组
        if r'\begin{cases}' in latex_input:
            return handle_system(latex_input)

        # 4. 检测不等式
        if re.search(r'[<>]=?|\\leq|\\geq|\\gtrless', latex_input):
            return solve_inequality(latex_input)

        # 转换为 SymPy 表达式
        expr = latex2sympy(latex_input)

        try:
            res = latex2latex(latex_input)
            if res.replace(' ','') == latex_input:
                res = latex(expr.evalf(32))

            return res
        except:
            # 处理简单表达式
            try:

                if expr.is_Number:
                    return latex(expr.evalf())

                factored = factor(expr)
                if factored != expr:
                    return latex(factored)

                simplified = simplify(expr)
                return latex(simplified)
            except:
                # 转换为 SymPy 表达式
                expr = latex2sympy(latex_input)
                return latex(expr)

    except Exception as e:
        if __name__ == '__main__':
            return r"\text{计算错误: " + str(e) + "}"
        else:
            return r"\text{计算失败}"

"""判断输入是否是潜在方程"""
def is_potential_equation(latex_input):

    # 必须有等号
    if '=' not in latex_input:
        return False

    # 尝试解析整个表达式
    try:
        expr = latex2sympy(latex_input)
        if isinstance(expr, Eq):
            return True
    except:
        pass

    # 尝试分割等号
    parts = [p.strip() for p in latex_input.split('=') if p.strip()]
    if len(parts) < 2:
        return False

    for index,istr in enumerate(latex_input):
        if istr == '=':
            # 尝试解析两边
            try:
                left_str = latex_input[:index].strip()
                right_str = latex_input[index + 1:].strip()

                # 如果两边都有内容，尝试解析
                if left_str and right_str:
                    lhs = latex2sympy(left_str)
                    rhs = latex2sympy(right_str)
                    return True
            except:
                pass

    return False

"""处理方程组或不等式组"""
def handle_system(latex_input):

    try:
        if re.search(r'[<>]=?|\\leq|\\geq|\\gtrless', latex_input):
            return solve_inequality_system(latex_input)
        else:
            return solve_equation_system(latex_input)
    except:
        return r"\text{无法解析方程组}"

"""求解单个方程"""
def solve_equation(latex_input):

    try:
        # 尝试解析为方程
        expr = latex2sympy(latex_input)

        # 如果不是方程，尝试添加等号
        if not isinstance(expr, Eq):
            if '=' in latex_input:
                for index, istr in enumerate(latex_input):
                    if istr == '=':# 尝试解析两边
                        try:
                            left_str = latex_input[:index].strip()
                            right_str = latex_input[index + 1:].strip()

                            # 如果两边都有内容，尝试解析
                            if left_str and right_str:
                                lhs = latex2sympy(left_str)
                                rhs = latex2sympy(right_str)
                                expr = Eq(lhs, rhs)
                        except:pass
            else:
                # 默认为等于零
                expr = Eq(expr, 0)

        # 尝试符号求解（带超时）
        result, timeout = run_with_timeout(
            _symbolic_solve_equation,
            (expr,),
            MAX_SYMBOLIC_TIME
        )

        if not timeout and result:
            return result

        # 符号求解失败，尝试数值求解
        return _numeric_solve_equation(expr)

    except Exception as e:
        if __name__ == '__main__':
            return r"\text{方程求解错误: " + str(e) + "}"
        else:
            return r'\text{方程求解错误}'

"""符号方法求解方程"""
def _symbolic_solve_equation(equation):

    # 提取变量
    variables = sorted(equation.free_symbols, key=lambda x: str(x))

    # 简化方程
    simplified_eq = simplify(equation)

    # 检查恒等式
    if simplified_eq == True:
        return r"\text{恒成立}"

    # 检查矛盾式
    if simplified_eq == False:
        return r"\text{无解}"

    # 检查恒等式（如 x + x = 2x）
    if simplify(simplified_eq.lhs - simplified_eq.rhs) == 0:
        domain = variables[0].domain if hasattr(variables[0], 'domain') else r"R"
        return f"{latex(variables[0])} \\in {domain} "


    if not variables:
        return r"\text{未找到变量}"

    # 尝试求解
    try:
        # 如果方程包含求和，尝试简化
        if any(isinstance(term, Sum) for term in preorder_traversal(equation)):
            # 尝试计算求和
            simplified_eq = equation.doit()
            solutions = solve(simplified_eq, variables, dict=True)
        else:
            solutions = solve(equation, variables, dict=True)

        if solutions is None or (isinstance(solutions, list) and len(solutions) == 0):
            return _numeric_solve_equation(equation)

        # 检查是否存在 CRootOf 对象（表示高阶方程）
        has_croot = any(
            isinstance(v, CRootOf)
            for sol in solutions
            for v in sol.values()
        )

        # 如果是高阶多项式方程，使用数值方法
        if has_croot and len(variables) == 1:
            poly = Poly(equation.lhs - equation.rhs, variables[0])
            if poly.degree() > 2:  # 3次及以上方程
                # 使用NumPy求解多项式方程
                return solve_polynomial_with_numpy(poly, variables[0])

        # 格式化解
        if isinstance(solutions, dict):
            # 单个解的情况
            return "\\".join(latex(Eq(k, v)) for k, v in solutions.items())
        elif len(solutions) == 1:
            sol = solutions[0]
            if len(sol) == 1:
                var = next(iter(sol.keys()))
                return latex(Eq(var, sol[var]))
            else:
                return "\\".join(latex(Eq(k, v)) for k, v in sol.items())
        else:
            return " \\ ".join(
                r"\left\{ " +
                ", ".join(f"{latex(k)} = {latex(v)}" for k, v in s.items()) +
                r" \right\}"
                for s in solutions
            )
    except NotImplementedError:
        return None
    except Exception as e:
        if __name__ == '__main__':
            return f"\\text{{符号求解错误: {str(e)}}}"
        else:
            return r'\text{方程求解错误}'

"""格式化多项式方程的根（包括实数根和复数根）"""
def format_polynomial_roots(poly, real_roots, complex_roots, var):

    # 构建多项式表达式
    poly_expr = latex(poly.as_expr())

    # 构建结果字符串
    result = ""
    roots = real_roots + complex_roots
    if len(roots) == 1:
        result += f"{latex(var)} = {roots[0]}"
    else:
        complex_str = ", ".join(format_complex(c) for c in roots)
        result += f"{latex(var)} \\in \\left\\{{{complex_str}\\right\\}}"
    '''
    # 添加实数根
    if real_roots:
        if len(real_roots) == 1:
            result += f"{latex(var)} = {real_roots[0]}"
        else:
            real_str = ", ".join(str(r) for r in real_roots)
            result += f"{latex(var)} \\in \\left\\{{{real_str}\\right\\}}"

    # 添加复数根
    if complex_roots:
        if real_roots:
            result += r" \\ "
        if len(complex_roots) == 1:
            result += f"{latex(var)} = {format_complex(complex_roots[0])}"
        else:
            complex_str = ", ".join(format_complex(c) for c in complex_roots)
            result += f"{latex(var)} \\in \\left\\{{{complex_str}\\right\\}}"
    '''
    return result

"""格式化复数为LaTeX格式"""
def format_complex(c):

    real = c.real
    imag = c.imag

    if imag == 0:
        return str(real)
    elif real == 0:
        return f"{imag}i" if imag > 0 else f"({imag})i"
    else:
        sign = "+" if imag >= 0 else ""
        return f"{real}{sign}{imag}i"

"""使用NumPy求解多项式方程，返回所有根"""
def solve_polynomial_with_numpy(poly, var):

    try:
        # 获取多项式系数（从最高次项到常数项）
        coeffs = poly.all_coeffs()

        # 使用NumPy计算所有根
        roots = np.roots(coeffs)

        # 分离实数根和复数根
        real_roots = []
        complex_roots = []

        for r in roots:
            # 保留6位小数
            real_part = round(r.real, 6)
            imag_part = round(r.imag, 6)

            if abs(imag_part) < 1e-6:
                # 实数根（虚部为0）
                real_roots.append(real_part)
            else:
                # 复数根
                # 避免显示 -0.0j
                if abs(real_part) < 1e-6:
                    real_part = 0.0
                if abs(imag_part) < 1e-6:
                    imag_part = 0.0

                # 以标准复数形式表示
                complex_roots.append(complex(real_part, imag_part))

        # 去重并排序（实数根按数值排序，复数根按实部、虚部排序）
        real_roots = sorted(set(real_roots))
        complex_roots = sorted(set(complex_roots), key=lambda x: (x.real, x.imag))

        # 格式化结果
        return format_polynomial_roots(poly, real_roots, complex_roots, var)

    except Exception as e:
        # 如果NumPy求解失败，使用其他数值方法
        return _numeric_solve_equation(Eq(poly.as_expr(), 0))

"""数值方法求解方程（支持积分）"""
def _numeric_solve_equation(equation):

    try:
        # 提取变量
        variables = sorted(equation.free_symbols, key=lambda x: str(x))

        if not variables:
            return r"\text{未找到变量}"

        # 将方程转换为 f(x) = 0 的形式
        f_expr = equation.lhs - equation.rhs

        # 定义数值求解函数
        def eq_func(x):
            try:
                # 替换变量并计算表达式
                return float(f_expr.subs({variables[0]: x[0]}))
            except:
                # 如果包含特殊函数（如积分），使用更安全的计算
                from sympy import lambdify
                func = lambdify(variables[0], f_expr, modules=['scipy'])
                return func(x[0])

        # 尝试不同初始值
        solutions = set()
        for guess in [0.1, 0.5, 1.0, 1.5, 2.0]:
            try:
                sol, infodict, ier, mesg = fsolve(eq_func, [guess], full_output=True)
                if ier == 1:  # 检查是否成功
                    # 验证解是否满足方程
                    val = eq_func(sol)
                    if abs(val) < 1e-6:
                        solutions.add(round(sol[0], 6))
            except:
                continue

        if not solutions:
            return r"\text{数值求解失败}"

        # 格式化解
        var = variables[0]
        if len(solutions) == 1:
            return latex(Eq(var, list(solutions)[0]))
        else:
            sol_str = ", ".join(str(s) for s in sorted(solutions))
            return f"{latex(var)} \\in \\left\\{{{sol_str}\\right\\}}"

    except Exception as e:
        if __name__ == '__main__':
            return r"\text{数值求解错误: " + str(e) + "}"
        else:
            return r'\text{方程求解错误}'

"""求解方程组"""
def solve_equation_system(latex_input):
    try:
        # 提取方程组
        if r'\begin{cases}' in latex_input:
            # 提取cases环境内容
            cases_match = re.search(r'\\begin{cases}(.*?)\\end{cases}', latex_input, re.DOTALL)
            if not cases_match:
                return r"\text{无法解析方程组格式}"

            equations_str = cases_match.group(1)
            # 分割方程 - 处理不同分隔符
            equations = [eq.strip() for eq in re.split(r'\\\\|\\\\.|\\n', equations_str) if eq.strip()]
        else:
            equations = [eq.strip() for eq in latex_input.split(',') if eq.strip()]

        # 转换所有方程为SymPy表达式
        sympy_eqs = []
        variables = set()

        for eq in equations:
            try:
                # 尝试解析为方程
                expr = latex2sympy(eq)
                if not isinstance(expr, Eq):
                    # 尝试添加等号
                    if '=' in eq:
                        parts = eq.split('=', 1)
                        lhs = latex2sympy(parts[0].strip())
                        rhs = latex2sympy(parts[1].strip())
                        expr = Eq(lhs, rhs)
                    else:
                        expr = Eq(expr, 0)
                sympy_eqs.append(expr)
                variables |= expr.free_symbols
            except:
                if __name__ == '__main__':
                    return r"\text{无法解析方程: " + eq + "}"
                else:
                    return r'\text{无法解析方程}'

        if not variables:
            return r"\text{未找到变量}"

        # 尝试符号求解
        result, timeout = run_with_timeout(
            _symbolic_solve_system,
            (sympy_eqs, list(variables)),
            MAX_SYMBOLIC_TIME
        )

        if not timeout and result:
            return result

        # 符号求解失败，尝试数值求解
        return _numeric_solve_system(sympy_eqs, list(variables))

    except Exception as e:
        if __name__ == '__main__':
            return r"\text{方程组求解错误: " + str(e) + "}"
        else:
            return r'\text{方程组求解错误}'

"""符号方法求解方程组"""
def _symbolic_solve_system(equations, variables):
    try:
        solutions = solve(equations, variables, dict=True)

        if solutions is None or (isinstance(solutions, list) and len(solutions) == 0):
            return r"\text{方程组无解}"

        # 格式化解
        if len(solutions) == 1:
            sol = solutions[0]
            return "\\".join(latex(Eq(k, v)) for k, v in sol.items())
        else:
            return " \\ ".join(
                r"\left\{ " +
                ", ".join(f"{latex(k)} = {latex(v)}" for k, v in s.items()) +
                r" \right\}"
                for s in solutions
            )
    except NotImplementedError:
        return None
    except Exception as e:
        if __name__ == '__main__':
            return f"\\text{{符号求解错误: {str(e)}}}"
        else:
            return r'\text{方程组求解错误}'

"""数值方法求解方程组"""
def _numeric_solve_system(equations, variables):

    try:
        # 定义数值求解函数
        def system_func(x):
            subs_dict = {var: val for var, val in zip(variables, x)}
            return [float(eq.lhs.subs(subs_dict)) - float(eq.rhs.subs(subs_dict)) for eq in equations]

        # 尝试不同初始值组合
        solutions = []
        for guess in [[0] * len(variables), [1] * len(variables), [-1] * len(variables)]:
            sol = root(system_func, guess, method='lm')
        if sol.success:
        # 四舍五入到小数点后6位
            rounded_sol = [round(val, 6) for val in sol.x]

        # 检查是否已存在类似解
        if not any(np.allclose(rounded_sol, existing_sol, atol=1e-4) for existing_sol in solutions):
            solutions.append(rounded_sol)

        if not solutions:
            return r"\text{数值求解失败}"

        # 格式化解
        result = []
        for i, sol in enumerate(solutions):
            sol_str = ", ".join(f"{latex(var)} = {val}" for var, val in zip(variables, sol))
            result.append(sol_str)

        return " \\ ".join(result)

    except:
        return r"\text{数值求解失败}"

"""求解单个不等式"""
def solve_inequality(latex_input):

    try:
        # 解析不等式
        expr = latex2sympy(latex_input)

        if not isinstance(expr, Relational):
            # 尝试解析为不等式
            if '>' in latex_input or '<' in latex_input:
                # 尝试添加不等号
                if '>' in latex_input:
                    parts = latex_input.split('>', 1)
                    lhs = latex2sympy(parts[0].strip())
                    rhs = latex2sympy(parts[1].strip())
                    expr = Gt(lhs, rhs)
                elif '<' in latex_input:
                    parts = latex_input.split('<', 1)
                    lhs = latex2sympy(parts[0].strip())
                    rhs = latex2sympy(parts[1].strip())
                    expr = Lt(lhs, rhs)
            else:
                return r"\text{输入不是不等式}"

        # 提取变量
        variables = expr.free_symbols
        if len(variables) != 1:
            return r"\text{仅支持单变量不等式}"

        var = next(iter(variables))

        # 尝试符号求解
        result, timeout = run_with_timeout(
            _symbolic_solve_inequality,
            (expr, var),
            MAX_SYMBOLIC_TIME
        )

        if not timeout and result:
            return result

        # 符号求解失败，尝试数值求解
        return _numeric_solve_inequality(expr, var)

    except Exception as e:
        if __name__ == '__main__':
            return r"\text{不等式求解错误: " + str(e) + "}"
        else:
            return r'\text{不等式求解错误}'

"""符号方法求解不等式"""
def _symbolic_solve_inequality(inequality, var):

    try:
        solution = reduce_inequalities(inequality, var)
        return latex(solution)
    except NotImplementedError:
        return None
    except Exception as e:
        if __name__ == '__main__':
            return f"\\text{{符号求解错误: {str(e)}}}"
        else:
            return r'\text{不等式求解错误}'

"""数值方法求解不等式"""
def _numeric_solve_inequality(inequality, var):

    try:
        # 定义函数
        f = inequality.lhs - inequality.rhs

        # 在关键点采样
        critical_points = [-100, -10, -1, 0, 1, 10, 100]
        solutions = []

        # 找到函数零点
        for i in range(len(critical_points) - 1):
            a, b = critical_points[i], critical_points[i + 1]

            # 检查区间端点
            fa = f.subs(var, a)
            fb = f.subs(var, b)

            # 如果函数在端点异号，说明区间内有解
            if fa * fb < 0:
                # 在区间内寻找零点
                def eq_func(x):
                    return float(f.subs(var, x[0]))

                root_val = fsolve(eq_func, [(a + b) / 2])[0]
                solutions.append(root_val)

        # 根据不等式类型确定解集
        if not solutions:
            return r"\text{无解}"

        solutions = sorted(solutions)

        if inequality.rel_op == '<':
            return f"{latex(var)} < {solutions[0]}"
        elif inequality.rel_op == '>':
            return f"{latex(var)} > {solutions[0]}"
        elif inequality.rel_op == '<=':
            return f"{latex(var)} \\leq {solutions[0]}"
        elif inequality.rel_op == '>=':
            return f"{latex(var)} \\geq {solutions[0]}"
        else:
            return r"\text{复杂不等式，无法数值求解}"

    except:
        return r"\text{数值求解失败}"

"""求解不等式组"""

def solve_inequality_system(latex_input):
    """求解多元不等式组"""
    try:
        # 提取不等式组
        if r'\begin{cases}' in latex_input:
            inequalities_str = re.findall(r'\\begin{cases}(.*?)\\end{cases}', latex_input, re.DOTALL)[0]
            inequalities = [ineq.strip() for ineq in re.split(r'\\\\|\n', inequalities_str) if ineq.strip()]
        else:
            inequalities = [ineq.strip() for ineq in latex_input.split(',') if ineq.strip()]

        # 转换所有不等式为SymPy表达式
        sympy_ineqs = []
        variables = set()

        for ineq in inequalities:
            expr = latex2sympy(ineq)
            if not isinstance(expr, Relational):
                # 尝试解析为不等式
                if '>' in ineq or '<' in ineq or '\\geq' in ineq or '\\leq' in ineq:
                    if '>' in ineq:
                        parts = ineq.split('>', 1)
                        lhs = latex2sympy(parts[0].strip())
                        rhs = latex2sympy(parts[1].strip())
                        expr = Gt(lhs, rhs)
                    elif '<' in ineq:
                        parts = ineq.split('<', 1)
                        lhs = latex2sympy(parts[0].strip())
                        rhs = latex2sympy(parts[1].strip())
                        expr = Lt(lhs, rhs)
                    elif '\\geq' in ineq:
                        parts = ineq.split('\\geq', 1)
                        lhs = latex2sympy(parts[0].strip())
                        rhs = latex2sympy(parts[1].strip())
                        expr = Ge(lhs, rhs)
                    elif '\\leq' in ineq:
                        parts = ineq.split('\\leq', 1)
                        lhs = latex2sympy(parts[0].strip())
                        rhs = latex2sympy(parts[1].strip())
                        expr = Le(lhs, rhs)
                else:
                    continue
            sympy_ineqs.append(expr)
            variables |= expr.free_symbols

        if not variables:
            return r"\text{未找到变量}"

        # 尝试符号求解
        result, timeout = run_with_timeout(
            _symbolic_solve_inequality_system,
            (sympy_ineqs, list(variables)),
            MAX_SYMBOLIC_TIME
        )

        if not timeout and result:
            return result

        # 符号求解失败，尝试数值求解
        return _numeric_solve_inequality_system(sympy_ineqs, list(variables))

    except Exception as e:
        return r"\text{不等式组求解错误: " + str(e) + "}"


def _symbolic_solve_inequality_system(inequalities, variables):
    """符号方法求解多元不等式组"""
    try:
        # 使用reduce_inequalities求解
        solution = reduce_inequalities(inequalities, variables)

        # 格式化解集
        return format_inequality_solution(solution)
    except NotImplementedError:
        # 尝试分步求解
        return _stepwise_solve_inequalities(inequalities, variables)
    except Exception as e:
        return f"\\text{{符号求解错误: {str(e)}}}"


def _stepwise_solve_inequalities(inequalities, variables):
    """分步求解不等式组（当直接求解失败时）"""
    try:
        # 尝试简化每个不等式
        simplified_ineqs = [simplify(ineq) for ineq in inequalities]

        # 尝试求解每个不等式
        solutions = []
        for ineq in simplified_ineqs:
            try:
                sol = reduce_inequalities([ineq], variables)
                solutions.append(sol)
            except:
                solutions.append(ineq)

        # 组合解集
        if len(solutions) == 1:
            return format_inequality_solution(solutions[0])

        # 创建逻辑表达式
        from sympy import And
        combined = And(*solutions)
        return latex(combined)
    except:
        # 如果失败，返回原始不等式
        return " \\land ".join(latex(ineq) for ineq in simplified_ineqs)


def _numeric_solve_inequality_system(inequalities, variables):
    """数值方法求解多元不等式组"""
    try:
        # 仅支持2个变量（可视化）
        if len(variables) > 2:
            return r"\text{仅支持最多2个变量的数值求解}"

        # 创建求解函数
        def satisfies(point):
            subs_dict = {var: val for var, val in zip(variables, point)}
            return all(ineq.subs(subs_dict) for ineq in inequalities)

        # 生成网格点
        if len(variables) == 1:
            # 单变量：区间搜索
            return _numeric_solve_inequality_system_1d(inequalities, variables[0])

        # 双变量：网格搜索
        return _numeric_solve_inequality_system_2d(inequalities, variables)

    except:
        return r"\text{数值求解失败}"


def _numeric_solve_inequality_system_1d(inequalities, var):
    """数值方法求解单变量不等式组"""
    try:
        # 在关键点采样
        critical_points = [-100, -10, -5, -2, -1, 0, 1, 2, 5, 10, 100]
        valid_intervals = []

        # 检查每个区间是否满足所有不等式
        for i in range(len(critical_points) - 1):
            a, b = critical_points[i], critical_points[i + 1]
            mid = (a + b) / 2

            satisfies = True
            for ineq in inequalities:
                # 检查中点是否满足不等式
                if not ineq.subs(var, mid):
                    satisfies = False
                    break

            if satisfies:
                valid_intervals.append((a, b))

        # 生成解集
        if not valid_intervals:
            return r"\text{无解}"

        solution_parts = []
        for a, b in valid_intervals:
            if a == -100 and b == 100:
                solution_parts.append(r"(-\\infty, \\infty)")
            elif a == -100:
                solution_parts.append(f"(-\\infty, {b})")
            elif b == 100:
                solution_parts.append(f"({a}, \\infty)")
            else:
                solution_parts.append(f"({a}, {b})")

        return f"{latex(var)}" + r" \in " + r" \cup ".join(solution_parts)

    except:
        return r"\text{数值求解失败}"


def _numeric_solve_inequality_system_2d(inequalities, variables):
    """数值方法求解双变量不等式组"""
    try:
        # 提取变量
        x, y = variables

        # 创建网格
        x_vals = np.linspace(-10, 10, 100)
        y_vals = np.linspace(-10, 10, 100)

        # 计算满足条件的点
        X, Y = np.meshgrid(x_vals, y_vals)
        Z = np.zeros_like(X, dtype=bool)

        for i in range(X.shape[0]):
            for j in range(X.shape[1]):
                point = {x: X[i, j], y: Y[i, j]}
                Z[i, j] = all(ineq.subs(point) for ineq in inequalities)

        # 提取边界点
        from matplotlib.path import Path
        from scipy.spatial import ConvexHull

        # 获取满足条件的点
        points = np.column_stack([X[Z], Y[Z]])

        if len(points) == 0:
            return r"\text{无解}"

        # 计算凸包
        hull = ConvexHull(points)
        hull_points = points[hull.vertices]

        # 创建多边形路径
        path = Path(hull_points)

        # 生成解的描述
        vertices_str = ", ".join(f"({x:.1f}, {y:.1f})" for x, y in hull_points)
        return f"{latex(x)} \\text{{ 和 }} {latex(y)} \\text{{ 满足: }} \\text{{凸包区域}} \\left[{vertices_str}\\right]"

    except:
        return r"\text{数值求解失败}"


def format_inequality_solution(solution):
    """格式化不等式组的解"""
    from sympy import And, Or, Interval, Union

    # 如果解是布尔值
    if solution == True:
        return r"\text{对所有变量成立}"
    if solution == False:
        return r"\text{无解}"

    # 如果解是逻辑表达式
    if isinstance(solution, (And, Or)):
        return latex(solution)

    # 如果解是区间或集合
    if isinstance(solution, (Interval, Union)):
        return latex(solution)

    # 尝试简化表达式
    simplified = simplify(solution)
    if simplified != solution:
        return latex(simplified)

    # 默认返回原始解
    return latex(solution)


"""处理矩阵表达式（包括矩阵运算）"""
def process_matrix(latex_input):

    try:
        # 先检查是否是矩阵方程
        if '=' in latex_input:
            # 如果是方程，交给方程求解函数处理
            return solve_equation(latex_input)

        # 转换整个表达式
        expr = latex2sympy(latex_input)

        # 尝试计算表达式
        try:
            result = expr.doit()
            if result != expr:
                return latex(result)
        except:
            pass

        # 特殊处理矩阵求逆
        if '^{-1}' in latex_input:
            try:
                matrix_expr = latex2sympy(re.sub(r'\^{-1}', '', latex_input))
                if hasattr(matrix_expr, 'inv'):
                    inverse = matrix_expr.inv()
                    return latex(inverse)
            except:
                pass

        # 特殊处理矩阵行列式
        if 'det' in latex_input or '\\det' in latex_input:
            try:
                clean_input = latex_input.replace(r'\det', '').replace('det', '')
                matrix_expr = latex2sympy(clean_input)
                if hasattr(matrix_expr, 'det'):
                    det = matrix_expr.det()
                    return latex(det)
            except:
                pass

        # 直接返回原始表达式
        return latex(expr)

    except Exception as e:
        if __name__ == '__main__':
            return f"\\text{{矩阵错误: {str(e)}}}"
        else:
            return r'\text{矩阵错误}'

"""带超时机制的函数执行（使用线程）"""
def run_with_timeout(func, args, timeout):

    result_queue = queue.Queue()

    def wrapper():
        try:
            result = func(*args)
            result_queue.put(result)
        except Exception as e:
            if __name__ == '__main__':
                result_queue.put(f"\\text{{执行错误: {str(e)}}}")
            else:
                result_queue.put(r"\\text{执行错误}")

    thread = threading.Thread(target=wrapper)
    thread.daemon = True  # 设置为守护线程，主线程结束时自动终止
    thread.start()

    # 等待线程完成或超时
    thread.join(timeout)

    if thread.is_alive():
        # 超时，无法终止线程但可以标记超时状态
        return None, True
    else:
        # 线程正常完成
        if not result_queue.empty():
            return result_queue.get(), False
        return None, True

if __name__ == "__main__":
    # 测试用例
    tests = [
        r"x^2 + 2x + 1",  # 代数化简
        r"\frac{d}{dx}(x^3 + 2x)",  # 导数


        r"x^2 - 4 = 0",  # 方程求解
        r"x^3 - 2x^2 + x = 0",  # 求解命令
        r"\sum _{n=1}^{\infty} \frac{1}{n^{2}}",  # 级数求和
        r'\sum ^{6}_{n=0}\frac{x^{n}}{n!}',
        r'\sum ^{2}_{i=1}\sum ^{2}_{j=1}\left(i+j\right)',
        r'\lim _{x\to0}\frac{\sin x}{x}',

        r"\begin{bmatrix} 1 & 2 \\ 3 & 4 \end{bmatrix}^{-1}",  # 矩阵求逆
        r'\det \begin{pmatrix}1 & 2 \\ 3 & 4 \end{pmatrix}',
        r"\begin{pmatrix} 1  \\ 2 \end{pmatrix}  \begin{pmatrix} 1 & 2 \end{pmatrix}",
        r"\begin{pmatrix} 1  \\ 2 \end{pmatrix}  \begin{pmatrix} x & 2 \end{pmatrix} = \begin{pmatrix} 1 & 2 \\ 2 & 4 \end{pmatrix}",
        r'\det\begin{bmatrix}2-x&1\\1&2-x\end{bmatrix}=0',
        # 矩阵方程

        # 方程
        r"x^2 - 4 = 0",
        r"x^3 - 2x^2 + x = 0",
        r"e^x + x = 5",  # 需要数值解

        # 方程组
        #r"\begin{cases} x + y = 5 \\ 2x - y = 1 \end{cases}",

        # 不等式
        r"x^2 - 3x + 2 > 0",
        r"\sin(x) \geq 0.5",

        # 不等式组
        r"\begin{cases} x > 0 \\ x < 10 \\ x^2 < 50 \end{cases}",
        #r"\begin{cases} 2x + 3y \leq 6 \\ x - y \geq 1 \end{cases}",
        r'\begin{cases}x > 0 \\ x < 5 \\ x ^ 2 < 10 \end{cases}',
        #r'\begin{cases} x + y > 2 \\ x - y < 1 \\ x > 0 \end{cases}',
        #r'\begin{cases} x^2 + y^2 < 4 \\ y > x^2 - 1 \\ x > -1 \end{cases}',

        # 复杂问题
        r'\sum ^ {n}_{i = 1}i ^ {3} = 36',
        #r'\sum_{i = 1} ^ {n}i = \frac{n(n + 1)}{2}',
        r'\sum ^ {k}_{n = 1}n = 6',
        r"\int_0^1 x^2  dx",  # 积分
        r"\int_0^x e^{-t^2} dt = 0.5",  # 需要数值解
        r'\int^{1}_{0}\int^{x}_{0}\left(x^{2}+y^{2}\right)dydx'
        r'\int^{\infty }_{0}t^{2}e^{-st}dt',
        r'\int^{+\infty }_{-\infty }x\frac{1}{\sqrt{2\pi }\sigma }e^{-\frac{\left(x-\mu \right)^{2}}{2\sigma ^{2}}}dx',
        r'\frac{1}{\pi }\int^{\pi }_{-\pi }xdx',
        
        r"x^5 - 3x^4 + 2x^3 - 5x^2 + 7x - 11 = 0",  # 高次方程

        #r"\begin{cases} 2x + y \leq 6 \\ x - y > 0 \end{cases}",  # 不等式组
        r"e^{i\pi} + 1",  # 欧拉公式
    ]
    te = [
        #r'\int^{2}_{0}\int_{0}^{\sqrt{4-x^{2}}}\left(x^{2}+y^{2}\right)dydx',
        r'\frac{\partial^2 u}{\partial x^2} + \frac{\partial^2 u}{\partial y^2} = 0',
        r'\frac{\partial^{2}}{\partialx\partialy}\left(x^{3}y^{4}\right)',


        r'\oint\frac{1}{z}dz',
    ]




    for i, test in enumerate(tests, 1):
        print(f"输入 {i}: {test}")
        start = time.time()
        result = latex_calculator(str(test))
        elapsed = time.time() - start
        print(f"结果: {result}")
        print(f"耗时: {elapsed:.2f}秒\n")



from transform import *

def calculation(expression):
    formula = ''
    for i in expression:
        formula += i

    latexexpress = transform(inputexpress=formula)
    print('=' * 200)
    print('计算输入:' + str(latexexpress))
    # ===============开始解算===============
    latexout = latex_calculator(latexexpress)

    print('计算结果:' + str(latexout))

    result = transform(latexexpress=latexout)

    # print('输入(字符串):' + formula)
    return result