from pathlib import Path

CLEAN_DIR = Path("data/clean_text")
OUT_DIR = Path("data/ciphered_text/rot13")
OUT_DIR.mkdir(parents = True, exist_ok = True)

ALPHABET = "abcdefghijklmnopqrstuvwxyz"

def encrypt(text):
    result = []
    for c in text:
        if c in ALPHABET:
            result.append(ALPHABET[(ALPHABET.index(c) + 13) % 26])
        else:
            result.append(c)
    return ''.join(result)

decrypt = encrypt

for file in CLEAN_DIR.glob("*.txt"):
    text = file.read_text(encoding = "utf-8")
    cipher = encrypt(text)
    out_name = f"{file.stem}_rot13.txt"
    (OUT_DIR / out_name).write_text(cipher, encoding="utf-8")
    print("Saved:", out_name)