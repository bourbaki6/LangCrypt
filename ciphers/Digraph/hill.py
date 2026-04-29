from pathlib import Path

CLEAN_DIR = Path("data/clean_text")
OUT_DIR = Path("data/ciphered_text/hill")
OUT_DIR.mkdir(parents = True, exist_ok = True)

ALPHABET = "abcdefghijklmnopqrstuvwxyz"


KEYS = [
    [[3, 3], [2, 5]],   
    [[6, 24], [1, 13]],
    [[17, 17], [5, 21]],
]

def mat_mul(matrix, vec, mod=26):
    return [(sum(matrix[r][c] * vec[c] for c in range(len(vec)))) % mod
            for r in range(len(matrix))]

def mat_inv_2x2(m, mod=26):
    a, b, c, d = m[0][0], m[0][1], m[1][0], m[1][1]
    det = (a * d - b * c) % mod
    
    det_inv = None
    for x in range(mod):
        if (det * x) % mod == 1:
            det_inv = x
            break
    if det_inv is None:
        raise ValueError("Matrix not invertible mod 26")
    return [[(d * det_inv) % mod, (-b * det_inv) % mod],
            [(-c * det_inv) % mod, (a * det_inv) % mod]]

def encrypt(text, key):
    n = len(key)
    letters = [c for c in text if c in ALPHABET]
    
    while len(letters) % n != 0:
        letters.append('x')
    result = []
    for i in range(0, len(letters), n):
        vec = [ALPHABET.index(letters[i + j]) for j in range(n)]
        out = mat_mul(key, vec)
        result.extend(ALPHABET[v] for v in out)
    return ''.join(result)

def decrypt(text, key):
    inv = mat_inv_2x2(key)
    return encrypt(text, inv)

for file in CLEAN_DIR.glob("*.txt"):
    text = file.read_text(encoding="utf-8")
    for idx, key in enumerate(KEYS):
        cipher = encrypt(text, key)
        out_name = f"{file.stem}_hill_{idx}.txt"
        (OUT_DIR / out_name).write_text(cipher, encoding="utf-8")
        print("Saved:", out_name)