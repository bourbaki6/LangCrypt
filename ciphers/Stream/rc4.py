from pathlib import Path

CLEAN_DIR = Path("data/clean_text")
OUT_DIR = Path("data/ciphered_text/rc4")
OUT_DIR.mkdir(parents=True, exist_ok=True)

KEYS = ["cipher", "language", "secret", "model", "neural"]

def ksa(key):
    key_bytes = [ord(c) for c in key]
    S = list(range(256))
    j = 0
    for i in range(256):
        j = (j + S[i] + key_bytes[i % len(key_bytes)]) % 256
        S[i], S[j] = S[j], S[i]
    return S

def prga(S):
    i = j = 0
    while True:
        i = (i + 1) % 256
        j = (j + S[i]) % 256
        S[i], S[j] = S[j], S[i]
        yield S[(S[i] + S[j]) % 256]

def encrypt(text, key):
    S = ksa(key)
    keystream = prga(S)
    result = []
    for c in text:
        result.append(chr(ord(c) ^ next(keystream)))
    return ''.join(result)

decrypt = encrypt

def encrypt_safe(text, key):

    S = ksa(key)
    keystream = prga(S)
    result = []
    for c in text:
        result.append(f"{ord(c) ^ next(keystream):02x}")
    return ' '.join(result)

for file in CLEAN_DIR.glob("*.txt"):
    text = file.read_text(encoding="utf-8")
    for key in KEYS:
        cipher = encrypt_safe(text, key)
        out_name = f"{file.stem}_rc4_{key}.txt"
        (OUT_DIR / out_name).write_text(cipher, encoding = "utf-8")
        print("Saved:", out_name)