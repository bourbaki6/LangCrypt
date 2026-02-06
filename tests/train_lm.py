from pathlib import Path
from language_model import CharNGramLM

lm = CharNGramLM(n = 3)

plaintext_dir = Path("data/plaintext_clean")

for file in plaintext_dir.iterdir():
    text = file.read_text()
    lm.train(text)

print("Language model trained")
