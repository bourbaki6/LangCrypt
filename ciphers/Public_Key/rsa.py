from pathlib import Path

CLEAN_DIR = Path("data/clean_text")
OUT_DIR = Path("data/ciphered_text/rsa")
OUT_DIR.mkdir(parents = True, exist_ok = True)


def is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True

def gcd(a, b):
    while b:
        a, b = b, a % b
    return a

def mod_inverse(e, phi):

    old_r, r = e, phi
    old_s, s = 1, 0
    while r != 0:
        q = old_r // r
        old_r, r = r, old_r - q * r
        old_s, s = s, old_s - q * s
    return old_s % phi

def generate_keypair(p, q):
    n = p * q
    phi = (p - 1) * (q - 1)
    e = 65537

    if gcd(e, phi) != 1:
        e = 3
    d = mod_inverse(e, phi)
    return (e, n), (d, n)  

def encrypt_text(text, public_key):
    e, n = public_key
    return [pow(ord(c), e, n) for c in text]

def decrypt_text(ciphertext, private_key):
    d, n = private_key
    return ''.join(chr(pow(c, d, n)) for c in ciphertext)

PRIME_PAIRS = [(61, 53), (89, 97), (101, 103)]

for file in CLEAN_DIR.glob("*.txt"):
    text = file.read_text(encoding = "utf-8")
    
    sample = text[:500]
    for idx, (p, q) in enumerate(PRIME_PAIRS):
        pub, priv = generate_keypair(p, q)
        cipher_ints = encrypt_text(sample, pub)
        cipher_str = ' '.join(str(x) for x in cipher_ints)
        out_name = f"{file.stem}_rsa_{idx}.txt"
        (OUT_DIR / out_name).write_text(cipher_str, encoding = "utf-8")
        print("Saved:", out_name)