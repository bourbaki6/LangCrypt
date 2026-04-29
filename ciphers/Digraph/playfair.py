from pathlib import Path

CLEAN_DIR = Path("data/clean_text")
OUT_DIR = Path("data/ciphered_text/playfair")
OUT_DIR.mkdir(parents=True, exist_ok=True)

KEYS = ["cipher", "language", "secret", "model", "neural"]

def build_square(key):
    
    seen = []
    for c in (key + "abcdefghiklmnopqrstuvwxyz"):
        if c == 'j':
            c = 'i'
        if c not in seen:
            seen.append(c)
    return [seen[i*5:(i+1)*5] for i in range(5)]

def find_pos(square, c):
    if c == 'j':
        c = 'i'
    for r, row in enumerate(square):
        if c in row:
            return r, row.index(c)
    raise ValueError(f"'{c}' not found in square")

def prepare(text):
    
    out = []
    for c in text:
        if c in "abcdefghijklmnopqrstuvwxyz":
            out.append('i' if c == 'j' else c)
    i = 0
    digraphs = []
    while i < len(out):
        a = out[i]
        if i + 1 == len(out):
            digraphs.append((a, 'x'))
            i += 1
        elif out[i + 1] == a:
            digraphs.append((a, 'x'))
            i += 1
        else:
            digraphs.append((a, out[i + 1]))
            i += 2
    return digraphs

def encrypt_pair(square, a, b):
    ra, ca = find_pos(square, a)
    rb, cb = find_pos(square, b)
    if ra == rb:
        return square[ra][(ca + 1) % 5] + square[rb][(cb + 1) % 5]
    elif ca == cb:
        return square[(ra + 1) % 5][ca] + square[(rb + 1) % 5][cb]
    else:
        return square[ra][cb] + square[rb][ca]

def decrypt_pair(square, a, b):
    ra, ca = find_pos(square, a)
    rb, cb = find_pos(square, b)
    if ra == rb:
        return square[ra][(ca - 1) % 5] + square[rb][(cb - 1) % 5]
    elif ca == cb:
        return square[(ra - 1) % 5][ca] + square[(rb - 1) % 5][cb]
    else:
        return square[ra][cb] + square[rb][ca]

def encrypt(text, key):
    square = build_square(key)
    pairs = prepare(text)
    return ''.join(encrypt_pair(square, a, b) for a, b in pairs)

def decrypt(text, key):
    square = build_square(key)
    pairs = [(text[i], text[i+1]) for i in range(0, len(text), 2)]
    return ''.join(decrypt_pair(square, a, b) for a, b in pairs)

for file in CLEAN_DIR.glob("*.txt"):
    text = file.read_text(encoding="utf-8")
    for key in KEYS:
        cipher = encrypt(text, key)
        out_name = f"{file.stem}_playfair_{key}.txt"
        (OUT_DIR / out_name).write_text(cipher, encoding="utf-8")
        print("Saved:", out_name)