keyboard = [
    ['z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '.', '/'],
    ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', ';'],
    ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p'],
    ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0']
]

def strum_to_key(strum):
    i, j = strum
    return keyboard[i][j]