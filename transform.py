left = ['frac{','^{','_{','(','^√{','√{','\\[','\\{']
right = ['frac}','^}','_}',')','^√}','√}','\\}', '\\]']

replacements = {r'frac{':r"\frac{", r'/':r'}{', r'frac}':r'}', '^}':'}', '_}':'}',r'^√{':r'\sqrt[', r'^√}':']', '√{':r'{', '√}':'}',
                '\\[':'\\left[','\\]':'\\right]',
                '[]':'', '^{^}':'', '_{_}':''}

keys = ['lim','log','lg','ln','sin','cos','tan','cot','sec','csc','sinh','cosh','tanh','coth','sech','csch','det',
    '×', '÷', '(',')','\\{','\\}','→', '∞','∮','∫', '％','°', '′', '″', '\\le ', '\\ge ',
    'α','β','γ','δ','ε','ζ','η','θ','ι','κ','λ','μ','ν','ξ','o','π','ρ','σ','τ','υ','φ','χ','ψ','ω',
    'Γ','Δ','Θ','Λ','Ξ','Π','Σ','Υ','Φ','Ψ','Ω','∈','·']

values = ['\\lim','\\log','\\log_{10}','\\ln ','\\sin ','\\cos ','\\tan ','\\cot ','\\sec ','\\csc ','\\sinh ','\\cosh ','\\tanh ','\\coth','\\sech','\\csch','\\det',
    r'\times', r'\div', '\\left(','\\right)','\\left\\{','\\right\\}', '\\to', '\\infty ',r'\oint',r'\int','\\%',
    r'\times \frac{\pi}{180}', r'\times \frac{\pi}{10800}', r'\times \frac{\pi}{648000}',
    '\\leq ', '\\geq ', r'\alpha ',r'\beta ',r'\gamma ',r'\delta ',r'\epsilon ',r'\zeta ',r'\eta ',r'\theta ',r'\iota ',r'\kappa ',
    r'\lambda ',r'\mu ',r'\nu ',r'\xi ',r'o',r'\pi ',r'\rho ',r'\sigma ',r'\tau ',r'\upsilon ',r'\phi ',
    r'\chi ',r'\psi ',r'\omega ',r'\Gamma ',r'\Delta ',r'\Theta ',r'\Lambda ',r'\Xi ',r'\Pi ',r'\Sigma ',r'\Upsilon ',r'\Phi ',r'\Psi ',r'\Omega ',
    r'\in',r'\cdot'
    ]

back_replacements = {r"\frac{":r'frac{', r'}{':r'/',r'\sqrt[':r'^√{', r'\sqrt{':r'^√{}√{', ']{':r'}√{', r'\sqrt[]{':r'^√{}√{',
                     r'\left[\begin{matrix}':r'\begin{bmatrix}', r'\end{matrix}\right]':r'\end{bmatrix}','\\left[':'[',r'\right]':']'
                     }


add = dict(zip(keys,values))
replacements.update(add)
#print(replacements)

back_add = dict(zip(values, keys))
back_replacements.update(back_add)
#print(back_replacements)

def find_occurrences(text, pattern):
    occurrences = []
    start = 0
    while True:
        index = text.find(pattern, start)
        if index == -1:
            break
        if pattern == '√{' and index != 0 and text[index - 1] + '√{' == '^√{':
                pass
        else:
            occurrences.append(index)
        start = index + 1
    return occurrences

def transform(inputexpress = None,latexexpress = None):
    if latexexpress == None:
        #print(inputexpress)
        for pattern, replacement in replacements.items():
            inputexpress = inputexpress.replace(pattern, replacement)
        #print(inputexpress)
        return inputexpress
    elif inputexpress == None:
        latexexpress = latexexpress.replace(r'\int\limits', r'\int')
        #print(latexexpress)
        for pattern, back_replacement in back_replacements.items():
            #print(pattern, back_replacement, pattern.replace(' ','') in latexexpress)
            latexexpress = latexexpress.replace(pattern.replace(' ',''), back_replacement)


        #print(latexexpress)

        res_f = find_occurrences(latexexpress, 'frac{')
        res_u = find_occurrences(latexexpress, '^{')
        res_d = find_occurrences(latexexpress, '_{')
        res_r = find_occurrences(latexexpress, '√{')
        res_ru = find_occurrences(latexexpress, '^√{')
        long_characters = [
        'lg', 'ln', 'lim', 'log', 'sin', 'cos', 'tan', 'cot', 'sec', 'csc', 'sinh', 'cosh', 'tanh', 'coth','sech', 'csch','det'
        '\\[',r'\]','\\{','\\}','\\leq ', '\\geq ','\\gg ', '\\ni ', '\\dashv ',
        '\\subset ', '\\supset ', '\\subseteq ', '\\supseteq ', '\\sqsubset ', '\\sqsupset ', '\\sqsubseteq ', '\\sqsupseteq ', ',',
        '\\sum ','\\prod ', '\\coprod ', '\\bigcup ', '\\bigcap ', '\\bigvee ', '\\bigwedge ',
        '\\mp ', '\\triangleleft ', '\\triangleright ',
        '\\cdot ', '\\setminus ', '\\star ', '\\ast ', '\\cup ' '\\cap ', '\\sqcup ', '\\sqcap ',
        '\\vee ', '\\wedge ', '\\circ ', '\\bullet ', '\\oplus ', '\\ominus ', '\\odot ', '\\oslash ',
        '\\otimes ', '\\bigcirc ', '\\diamond ', '\\uplus ', '\\bigtriangleup ', '\\bigtriangledown ',
        '\\lhd ', '\\rhd ', '\\unlhd ', '\\unrhd ', '\\amalg ', '\\wr ', '\\dagger ', '\\ddagger ',
        '\\rightleftharpoons ', '\\le ', '\\ge ',r'\begin{cases}',r'\end{cases}',r'\begin{pmatrix}',r'\end{pmatrix}',
               r'\begin{bmatrix}',r'\end{bmatrix}',r'\begin{vmatrix}',r'\end{vmatrix}',
                r'\begin{Vmatrix}',r'\end{Vmatrix}',r'\begin{Bmatrix}',r'\end{Bmatrix}',r'\begin{matrix}',r'\end{matrix}',
        r'\\',r'\text'

        ]
        res = [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]
        for w in long_characters:
            res[len(w)] += find_occurrences(latexexpress, w)
        wait_ba = []
        lis_answer = []
        i = 0
        while i < len(latexexpress):
            for j in range(len(res)):
                if i in res[j]:
                    lis_answer.append(latexexpress[i:i + j])
                    i += j
            if i >= len(latexexpress):break
            if i in res_u:
                wait_ba.append('^}')
                lis_answer.append(latexexpress[i:i+2])
                i += 2
            elif i in res_d:
                wait_ba.append('_}')
                lis_answer.append(latexexpress[i:i+2])
                i += 2
            elif i in res_ru:
                wait_ba.append('^√}')
                lis_answer.append(latexexpress[i:i + 3])
                i += 3
            elif i in res_r:
                wait_ba.append('√}')
                lis_answer.append(latexexpress[i:i + 2])
                i += 2
            elif i in res_f:
                wait_ba.append('frac}')
                lis_answer.append(latexexpress[i:i + 5])
                i += 5

            elif latexexpress[i] == '{':
                wait_ba.append('}')
                i +=1
            elif latexexpress[i] == '}':
                if wait_ba != []:
                    if wait_ba[-1] != '}':
                        lis_answer.append(wait_ba[-1])
                    wait_ba.pop(-1)
                i += 1
            elif latexexpress[i] in [' ']:
                i += 1
            else:
                lis_answer.append(latexexpress[i])
                i += 1

        #print(lis_answer)
        #print('='*200)
        return lis_answer

if __name__ == "__main__":
    print(transform(latexexpress = r'\int\limits_{0}^{\infty}'))
    print(transform(inputexpress = r'×'))