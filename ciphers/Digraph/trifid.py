from pathlib import Path

CLEAN_DIR = Path("data/clean_text")
OUT_DIR = Path("data/ciphered_text/trifid")
OUT_DIR.mkdir(parents=True, exist_ok=True)

KEYS = ["cipher", "language", "secret", "model", "neural"]

def build_cube(key):
    seen = []
    for c in (key + "abcdefghijklmnopqrstuvwxyz#"):
        if c not in seen:
            seen.append(c)
    return seen  

def pos(cube, c):
    idx = cube.index(c)
    return idx // 9, (idx % 9) // 3, idx % 3

def from_pos(cube, layer, row, col):
    return cube[layer * 9 + row * 3 + col]

def encrypt(text, key):
    cube = build_cube(key)
    letters = [c for c in text if c in "abcdefghijklmnopqrstuvwxyz"]
    layers, rows, cols = [], [], []
    for c in letters:
        l, r, col = pos(cube, c)
        layers.append(l)
        rows.append(r)
        cols.append(col)
    combined = layers + rows + cols
    n = len(letters)
    result = []
    for i in range(n):
        result.append(from_pos(cube, combined[i], combined[n + i], combined[2 * n + i]))
    return ''.join(result)

def decrypt(text, key):
    cube = build_cube(key)
    letters = [c for c in text if c in "abcdefghijklmnopqrstuvwxyz"]
    n = len(letters)
    nums = []
    for c in letters:
        l, r, col = pos(cube, c)
        nums.extend([l, r, col])
    layers = nums[0:n]
    rows   = nums[n:2*n]
    cols   = nums[2*n:3*n]
    result = []
    for i in range(n):
        result.append(from_pos(cube, layers[i], rows[i], cols[i]))
    return ''.join(result)

for file in CLEAN_DIR.glob("*.txt"):
    text = file.read_text(encoding="utf-8")
    for key in KEYS:
        cipher = encrypt(text, key)
        out_name = f"{file.stem}_trifid_{key}.txt"
        (OUT_DIR / out_name).write_text(cipher, encoding="utf-8")
        print("Saved:", out_name)