from pathlib import Path

CLEAN_DIR = Path("data/clean_text")
OUT_DIR = Path("data/ciphered_text/affine")
OUT_DIR.mkdir(parents = True, exist_ok = True)

ALPHABET = "abcdefghijklmnopqrstuvwxyz"

KEYS = [(3, 5), (5, 8), (7, 3), (11, 4), (17, 20), (25, 1)]

def mod_inverse(a, m=26):
    for x in range(1, m):
        if (a * x) % m == 1:
            return x
    raise ValueError(f"{a} has no inverse mod {m}")

def encrypt(text, a, b):
    result = []
    for c in text:
        if c in ALPHABET:
            x = ALPHABET.index(c)
            result.append(ALPHABET[(a * x + b) % 26])
        else:
            result.append(c)
    return ''.join(result)

def decrypt(text, a, b):
    a_inv = mod_inverse(a)
    result = []
    for c in text:
        if c in ALPHABET:
            y = ALPHABET.index(c)
            result.append(ALPHABET[(a_inv * (y - b)) % 26])
        else:
            result.append(c)
    return ''.join(result)

for file in CLEAN_DIR.glob("*.txt"):
    text = file.read_text(encoding="utf-8")
    for a, b in KEYS:
        cipher = encrypt(text, a, b)
        out_name = f"{file.stem}_affine_{a}_{b}.txt"
        (OUT_DIR / out_name).write_text(cipher, encoding = "utf-8")
        print("Saved:", out_name)