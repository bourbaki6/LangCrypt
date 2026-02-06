from pathlib import Path
import string

ALPHABET = string.ascii_lowercase

CLEAN_DIR = Path("data/clean_text")
CIPHER_DIR = Path("data/ciphered_text/caesar")

print("Looking for clean files in:", CLEAN_DIR.resolve())

files = list(CLEAN_DIR.glob("*.txt"))
print("Found files:", files)

CIPHER_DIR.mkdir(parents=True, exist_ok=True)

def encrypt(text, shift):
    result = []
    for c in text:
        if c in ALPHABET:
            i = (ALPHABET.index(c) + shift) % 26
            result.append(ALPHABET[i])
        else:
            result.append(c)
    return ''.join(result)

for file in files:
    text = file.read_text(encoding="utf-8")

    for shift in range(1, 26):
        cipher_text = encrypt(text, shift)

        out_name = f"{file.stem}_shift_{shift:02}.txt"
        out_file = CIPHER_DIR / out_name
        out_file.write_text(cipher_text, encoding="utf-8")

        print("Saved:", out_file)