import random

WORDFILE = "dictionary/countries.txt"
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

def get_random_word(WORDFILE):
    """Get a random word from the wordlist using no extra memory."""
    num_words_processed = 0
    curr_word = None
    with open(WORDFILE, 'r') as f:
        for word in f:
            word = word.strip().lower()
            num_words_processed += 1
            if random.randint(1, num_words_processed) == 1:
                curr_word = word
    return curr_word