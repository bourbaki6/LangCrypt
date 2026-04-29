from pathlib import Path

CLEAN_DIR = Path("data/clean_text")
OUT_DIR = Path("data/ciphered_text/railfence")
OUT_DIR.mkdir(parents = True, exist_ok = True)

RAILS = [2, 3, 4]

def encrypt(text, n_rails):
    rails = [[] for _ in range(n_rails)]
    rail = 0
    direction = 1
    for c in text:
        rails[rail].append(c)
        if rail == 0:
            direction = 1
        elif rail == n_rails - 1:
            direction = -1
        rail += direction
    return ''.join(''.join(r) for r in rails)

def decrypt(cipher, n_rails):
    n = len(cipher)
    
    pattern = []
    rail = 0
    direction = 1
    for _ in range(n):
        pattern.append(rail)
        if rail == 0:
            direction = 1
        elif rail == n_rails - 1:
            direction = -1
        rail += direction

    counts = [pattern.count(r) for r in range(n_rails)]
    
    rails = []
    idx = 0
    for c in counts:
        rails.append(list(cipher[idx:idx + c]))
        idx += c
    
    result = []
    pointers = [0] * n_rails
    
    for r in pattern:
        result.append(rails[r][pointers[r]])
        pointers[r] += 1
    return ''.join(result)

for file in CLEAN_DIR.glob("*.txt"):
    text = file.read_text(encoding="utf-8")
    for n in RAILS:
        cipher = encrypt(text, n)
        out_name = f"{file.stem}_rail_{n}.txt"
        (OUT_DIR / out_name).write_text(cipher, encoding="utf-8")
        print("Saved:", out_name)