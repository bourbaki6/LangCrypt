from pathlib import Path
import struct

CLEAN_DIR = Path("data/clean_text")
OUT_DIR = Path("data/ciphered_text/chacha20")
OUT_DIR.mkdir(parents = True, exist_ok = True)

KEYS = ["cipher", "language", "secret", "model", "neural"]

def pad_key(key, length=32):
    key_bytes = key.encode("utf-8")
    return (key_bytes * (length // len(key_bytes) + 1))[:length]

def rotl32(v, n):
    return ((v << n) | (v >> (32 - n))) & 0xFFFFFFFF

def quarter_round(a, b, c, d):
    a = (a + b) & 0xFFFFFFFF; d ^= a; d = rotl32(d, 16)
    c = (c + d) & 0xFFFFFFFF; b ^= c; b = rotl32(b, 12)
    a = (a + b) & 0xFFFFFFFF; d ^= a; d = rotl32(d, 8)
    c = (c + d) & 0xFFFFFFFF; b ^= c; b = rotl32(b, 7)
    return a, b, c, d

def chacha20_block(key_bytes, counter, nonce_bytes):
    constants = b"expa" b"nd 3" b"2-by" b"te k"
    state = list(struct.unpack("<16I",
        constants +
        key_bytes[:32] +
        struct.pack("<I", counter) +
        nonce_bytes[:12]
    ))
    working = state[:]
    for _ in range(10):  
        working[0], working[4], working[8],  working[12] = quarter_round(working[0], working[4], working[8],  working[12])
        working[1], working[5], working[9],  working[13] = quarter_round(working[1], working[5], working[9],  working[13])
        working[2], working[6], working[10], working[14] = quarter_round(working[2], working[6], working[10], working[14])
        working[3], working[7], working[11], working[15] = quarter_round(working[3], working[7], working[11], working[15])
        working[0], working[5], working[10], working[15] = quarter_round(working[0], working[5], working[10], working[15])
        working[1], working[6], working[11], working[12] = quarter_round(working[1], working[6], working[11], working[12])
        working[2], working[7], working[8],  working[13] = quarter_round(working[2], working[7], working[8],  working[13])
        working[3], working[4], working[9],  working[14] = quarter_round(working[3], working[4], working[9],  working[14])
    return struct.pack("<16I", *[(working[i] + state[i]) & 0xFFFFFFFF for i in range(16)])

def encrypt_safe(text, key):
    key_bytes = pad_key(key, 32)
    nonce = b"\x00" * 12
    text_bytes = text.encode("utf-8")
    result = []
    for block_idx in range(0, len(text_bytes), 64):
        keystream = chacha20_block(key_bytes, block_idx // 64, nonce)
        chunk = text_bytes[block_idx:block_idx + 64]
        for tb, kb in zip(chunk, keystream):
            result.append(f"{tb ^ kb:02x}")
    return ' '.join(result)

for file in CLEAN_DIR.glob("*.txt"):
    text = file.read_text(encoding="utf-8")
    for key in KEYS:
        cipher = encrypt_safe(text, key)
        out_name = f"{file.stem}_chacha20_{key}.txt"
        (OUT_DIR / out_name).write_text(cipher, encoding = "utf-8")
        print("Saved:", out_name)