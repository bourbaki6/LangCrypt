from pathlib import Path
import random

CLEAN_DIR = Path("data/clean_text")
OUT_DIR = Path("data/ciphered_text/transposition")
OUT_DIR.mkdir(parents=True, exist_ok=True)

def transpose(text, width):
    rows = [text[i:i+width] for i in range(0, len(text), width)]
    cols = ["".join(row[i] for row in rows if i < len(row)) for i in range(width)]
    return "".join(cols)

for file in CLEAN_DIR.glob("*.txt"):
    text = file.read_text(encoding="utf-8")

    for w in [5, 7, 9, 11]:  
        cipher = transpose(text, w)

        out_name = f"{file.stem}_trans_{w}.txt"
        (OUT_DIR / out_name).write_text(cipher, encoding="utf-8")

        print("Saved:", out_name)