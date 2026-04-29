from pathlib import Path

CLEAN_DIR = Path("data/clean_text")
OUT_DIR = Path("data/ciphered_text/bifid")
OUT_DIR.mkdir(parents=True, exist_ok=True)

KEYS = ["cipher", "language", "secret", "model", "neural"]

def build_square(key):
    seen = []
    for c in (key + "abcdefghiklmnopqrstuvwxyz"):
        if c == 'j':
            c = 'i'
        if c not in seen:
            seen.append(c)
    return seen  

def pos(square, c):
    if c == 'j':
        c = 'i'
    idx = square.index(c)
    return idx // 5, idx % 5

def encrypt(text, key):
    square = build_square(key)
    letters = [('i' if c == 'j' else c) for c in text if c in "abcdefghijklmnopqrstuvwxyz"]
    rows, cols = [], []
    for c in letters:
        r, col = pos(square, c)
        rows.append(r)
        cols.append(col)
    combined = rows + cols
    result = []
    for i in range(0, len(combined), 2):
        r1, r2 = combined[i], combined[i + 1]
        result.append(square[r1 * 5 + r2])  
  
    rows2, cols2 = [], []
    for i in range(0, len(combined) // 2, 1):
        rows2.append(combined[i])
        cols2.append(combined[len(combined) // 2 + i])
    result = []
    for r, c in zip(rows2, cols2):
        result.append(square[r * 5 + c])
    return ''.join(result)

def decrypt(text, key):
    square = build_square(key)
    letters = [c for c in text if c in "abcdefghiklmnopqrstuvwxyz"]
    n = len(letters)
    pairs = []
    for c in letters:
        r, col = pos(square, c)
        pairs.append(r)
        pairs.append(col)
    rows = pairs[0::2]
    cols = pairs[1::2]
    combined = rows[:n] + cols[:n]
    plain = []
    for i in range(n):
        r = combined[i]
        c = combined[n + i]
        plain.append(square[r * 5 + c])
    return ''.join(plain)

for file in CLEAN_DIR.glob("*.txt"):
    text = file.read_text(encoding="utf-8")
    for key in KEYS:
        cipher = encrypt(text, key)
        out_name = f"{file.stem}_bifid_{key}.txt"
        (OUT_DIR / out_name).write_text(cipher, encoding="utf-8")
        print("Saved:", out_name)