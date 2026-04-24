

import math
from collections import Counter
from pathlib import Path

class FrequencyModel:

    def __init__(self, smoothing: float = 0.01):

        self.smoothing = smoothing
        self.counts = Counter()
        self.total = 0

    def train(self, text: str):
        for ch in text:
            if ch.isalpha():
                self.counts[ch] += 1
                self.total += 1

    def train_from_dir(self, clean_dir: str):
        for path in Path(clean_dir).glob("*.txt"):
            self.train(path.read_text(encoding="utf-8"))

    def log_prob(self, char: str) -> float:

        vocab_size = 26
        numerator  = self.counts.get(char, 0) + self.smoothing
        denominator = self.total + self.smoothing * vocab_size
        return math.log(numerator / denominator)

    def score_text(self, text: str) -> float:
        
        return sum(self.log_prob(ch) for ch in text if ch.isalpha())


