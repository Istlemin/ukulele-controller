keyboard = [
    ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0'],
    ['z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '.', '/'],
    ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', ';'],
    ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p'],
]

def strum_to_key(strum):
    i, j = strum
    try:
        c = keyboard[i][j]
    except IndexError:
        c = None
    return c