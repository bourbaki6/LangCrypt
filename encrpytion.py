from pathlib import Path
from preprocess import normalize
from ciphers.caesar import encrypt as caesar
from ciphers.substitution import encrypt as sub_encrypt, random_key
from ciphers.vigenere import encrypt as vig_encrypt
from ciphers.transposition import encrypt as trans_encrypt

plaintext_dir = Path("data/plaintext")
ciphertext_dir = Path("data/ciphertext")

for file in plaintext_dir.iterdir():
    
    text = normalize(file.read_text())


    (ciphertext_dir / "caesar").mkdir(parents=True, exist_ok=True)
    (ciphertext_dir / "caesar" / file.name).write_text(caesar(text, 7))

    key = random_key()
    (ciphertext_dir / "substitution").mkdir(parents=True, exist_ok=True)
    (ciphertext_dir / "substitution" / file.name).write_text(sub_encrypt(text, key))

    (ciphertext_dir / "vigenere").mkdir(parents=True, exist_ok=True)
    (ciphertext_dir / "vigenere" / file.name).write_text(vig_encrypt(text, "logic"))

    (ciphertext_dir / "transposition").mkdir(parents=True, exist_ok=True)
    (ciphertext_dir / "transposition" / file.name).write_text(trans_encrypt(text, 8))
