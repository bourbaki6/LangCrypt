from pathlib import Path

CLEAN_DIR = Path("data/clean_text")
OUT_DIR = Path("data/ciphered_text/autokey")
OUT_DIR.mkdir(parents = True, exist_ok = True)

ALPHABET = "abcdefghijklmnopqrstuvwxyz"

KEYS = ["cipher", "language", "secret", "model", "neural"]

def encrypt(text, primer):
    result = []
    key_stream = list(primer)
    for c in text:
        if c in ALPHABET:
            key_stream.append(c)          
            shift = ALPHABET.index(key_stream.pop(0))
            result.append(ALPHABET[(ALPHABET.index(c) + shift) % 26])
        else:
            result.append(c)
    return ''.join(result)

def decrypt(text, primer):
    result = []
    key_stream = list(primer)
    for c in text:
        if c in ALPHABET:
            shift = ALPHABET.index(key_stream.pop(0))
            plain = ALPHABET[(ALPHABET.index(c) - shift) % 26]
            key_stream.append(plain)       
            result.append(plain)
        else:
            result.append(c)
    return ''.join(result)

for file in CLEAN_DIR.glob("*.txt"):
    text = file.read_text(encoding = "utf-8")
    for key in KEYS:
        cipher = encrypt(text, key)
        out_name = f"{file.stem}_autokey_{key}.txt"
        (OUT_DIR / out_name).write_text(cipher, encoding = "utf-8")
        print("Saved:", out_name)