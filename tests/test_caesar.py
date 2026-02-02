import string
from pathlib import Path
from language_model import CharNGramLM
from ciphers.caesar import encrypt

ALPHABET = string.ascii_lowercase

lm = CharNGramLM(n=3)

for file in Path("data/plaintext_clean").iterdir():
    lm.train(file.read_text())

ciphertext = Path("data/ciphertext/tryst/caesar_7.txt").read_text()

scores = []

for shift in range(26):
    candidate = encrypt(ciphertext, -shift)
    score = lm.score(candidate)
    scores.append((shift, score))

scores.sort(key=lambda x: x[1], reverse=True)

for shift, score in scores[:5]:
    print(f"Shift {shift}: score {score}")
