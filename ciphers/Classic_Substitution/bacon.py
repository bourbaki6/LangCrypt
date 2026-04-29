#---original binary cipher with a = 0, b = 1---#

from pathlib import Path

CLEAN_DIR = Path("data/clean_text")
OUT_DIR = Path("data/ciphered_text/bacon")
OUT_DIR.mkdir(parents=True, exist_ok=True)

ALPHABET = "abcdefghijklmnopqrstuvwxyz"

CODE = {
    'a': 'aaaaa', 'b': 'aaaab', 'c': 'aaaba', 'd': 'aaabb', 'e': 'aabaa',
    'f': 'aabab', 'g': 'aabba', 'h': 'aabbb', 'i': 'abaaa', 'j': 'abaab',
    'k': 'ababa', 'l': 'ababb', 'm': 'abbaa', 'n': 'abbab', 'o': 'abbba',
    'p': 'abbbb', 'q': 'baaaa', 'r': 'baaab', 's': 'baaba', 't': 'baabb',
    'u': 'babaa', 'v': 'babab', 'w': 'babba', 'x': 'babbb', 'y': 'bbaaa',
    'z': 'bbaab'
}

DECODE = {v: k for k, v in CODE.items()}

def encrypt(text):
    result = []
    for c in text:
        if c in CODE:
            result.append(CODE[c])
        elif c == ' ':
            result.append(' ')
        
    return ' '.join(result) if result else ''

def decrypt(text):
    result = []
    for token in text.split(' '):
        if token in DECODE:
            result.append(DECODE[token])
        elif token == '':
            result.append(' ')
    return ''.join(result)

for file in CLEAN_DIR.glob("*.txt"):
    text = file.read_text(encoding="utf-8")
    cipher = encrypt(text)
    out_name = f"{file.stem}_bacon.txt"
    (OUT_DIR / out_name).write_text(cipher, encoding = "utf-8")
    print("Saved:", out_name)