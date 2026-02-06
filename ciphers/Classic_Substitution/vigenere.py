from pathlib import Path
import string

ALPHABET = string.ascii_lowercase

CLEAN_DIR = Path("data/clean_text")
OUT_DIR = Path("data/ciphered_text/vigenere")
OUT_DIR.mkdir(parents=True, exist_ok=True)

WORDS = ["cipher", "language", "secret", "model", "neural"]

def vigenere(text, key):
    result = []
    k = 0
    for c in text:
        if c in ALPHABET:
            shift = ALPHABET.index(key[k % len(key)])
            i = (ALPHABET.index(c) + shift) % 26
            result.append(ALPHABET[i])
            k += 1
        else:
            result.append(c)
    return "".join(result)

for file in CLEAN_DIR.glob("*.txt"):
    text = file.read_text(encoding="utf-8")

    for key in WORDS:
        cipher = vigenere(text, key)

        out_name = f"{file.stem}_vig_{key}.txt"
        (OUT_DIR / out_name).write_text(cipher, encoding="utf-8")

        print("Saved:", out_name)