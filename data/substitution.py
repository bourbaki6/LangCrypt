from pathlib import Path
import string
import random

ALPHABET = string.ascii_lowercase

CLEAN_DIR = Path("data/clean_text")
OUT_DIR = Path("data/ciphered_text/substitution")
OUT_DIR.mkdir(parents=True, exist_ok=True)

def random_key():
    letters = list(ALPHABET)
    random.shuffle(letters)
    return dict(zip(ALPHABET, letters))

def encrypt(text, key):
    return "".join(key.get(c, c) for c in text)

for file in CLEAN_DIR.glob("*.txt"):
    text = file.read_text(encoding="utf-8")

    for i in range(10):  #---10 random substitutions per file---#
        key = random_key()
        cipher = encrypt(text, key)

        out_name = f"{file.stem}_sub_{i:02}.txt"
        (OUT_DIR / out_name).write_text(cipher, encoding="utf-8")

        print("Saved:", out_name)