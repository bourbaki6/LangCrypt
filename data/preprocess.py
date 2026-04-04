#---test cleaning lib- re ---#

import os
from pathlib import Path
import re
import unicodedata

RAW_DIR = Path("data/raw_text")
CLEAN_DIR = Path("data/clean_text")

CLEAN_DIR.mkdir(parents=True, exist_ok=True)

def normalize(text: str) -> str:
    text = text.lower()
    text = unicodedata.normalize("NFKD", text)
    text = ''.join(c for c in text if not unicodedata.combining(c))
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^a-z ]', '', text)
    return text.strip()

for file in RAW_DIR.glob("*.txt"):
    raw_text = file.read_text(encoding="utf-8")
    clean_text = normalize(raw_text)

    out_file = CLEAN_DIR / file.name
    out_file.write_text(clean_text, encoding="utf-8")

    print(f"Cleaned: {file.name}")