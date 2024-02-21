import random

easy = {'number of digits':2, 'operators':['+', '-'], 'number of problems':10}
medium = {'number of digits':2, 'operators':['+', '-', '/', '*'], 'number of problems':10}
medium_hard = {'number of digits':3, 'operators':['+', '-'], 'number of problems':10}
hard = {'number of digits':3, 'operators':['+', '-', '/', '*'], 'number of problems':10}

def generate_problems(level):
    if level==1:
        settings = easy
    elif level==2:
        settings = medium
    elif level==3:
        settings = medium_hard
    elif level==4:
        settings = hard
    problems = []
    for i in range(settings['number of problems']):
        a = random.randint(0, 10**settings['number of digits'])
        b = random.randint(0, 10**settings['number of digits'])
        op = random.choice(settings['operators'])
        if op=='+':
            result = a + b
        elif op=='-':
            result = a - b
        elif op=='*':
            result = a * b
        elif op=='/':
            result = random.randint(0, 10)
            b = result * a
        problems.append([a, b, op, result])
    return problems