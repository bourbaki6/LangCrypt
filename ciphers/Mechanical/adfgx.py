from pathlib import Path

CLEAN_DIR = Path("data/clean_text")
OUT_DIR = Path("data/ciphered_text/adfgx")
OUT_DIR.mkdir(parents=True, exist_ok=True)

ALPHABET = "abcdefghijklmnopqrstuvwxyz"
ADFGX = "adfgx"

KEYS = [("cipher", "language"), ("secret", "model"), ("neural", "crypto")]

def build_square(key):
    seen = []
    for c in (key + "abcdefghiklmnopqrstuvwxyz"):
        if c == 'j':
            c = 'i'
        if c not in seen:
            seen.append(c)
    return seen  

def encrypt(text, polybius_key, transposition_key):
    square = build_square(polybius_key)
    
    interim = []
    for c in text:
        if c in ALPHABET:
            c = 'i' if c == 'j' else c
            idx = square.index(c)
            row, col = idx // 5, idx % 5
            interim.append(ADFGX[row])
            interim.append(ADFGX[col])
        

    n_cols = len(transposition_key)
    order = sorted(range(n_cols), key=lambda i: transposition_key[i])
    cols = [[] for _ in range(n_cols)]
    for i, ch in enumerate(interim):
        cols[i % n_cols].append(ch)
    result = []
    for o in order:
        result.extend(cols[o])
    return ''.join(result)

def decrypt(text, polybius_key, transposition_key):
    n_cols = len(transposition_key)
    order = sorted(range(n_cols), key=lambda i: transposition_key[i])
    n = len(text)
    col_len = n // n_cols
    extra = n % n_cols
    
    lengths = [col_len + (1 if order.index(i) < extra else 0) for i in range(n_cols)]
    cols = {}
    idx = 0
    for o in order:
        cols[o] = list(text[idx:idx + lengths[o]])
        idx += lengths[o]
    interim = []
    for i in range(max(len(c) for c in cols.values())):
        for c in range(n_cols):
            if i < len(cols[c]):
                interim.append(cols[c][i])
    # polybius reverse
    square = build_square(polybius_key)
    result = []
    for i in range(0, len(interim), 2):
        r = ADFGX.index(interim[i])
        c = ADFGX.index(interim[i + 1])
        result.append(square[r * 5 + c])
    return ''.join(result)

for file in CLEAN_DIR.glob("*.txt"):
    text = file.read_text(encoding="utf-8")
    for pk, tk in KEYS:
        cipher = encrypt(text, pk, tk)
        out_name = f"{file.stem}_adfgx_{pk}.txt"
        (OUT_DIR / out_name).write_text(cipher, encoding="utf-8")
        print("Saved:", out_name)