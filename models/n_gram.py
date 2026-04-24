
import math
from collections import defaultdict
from pathlib import Path

class Ngram:

    def __init__(self, n: int, smoothing: float = 0.01):

        self.n = n
        self.smoothing = smoothing
        self.counts = self.counts
        self.vocab  = set()

    def train(self, text: str):

        for i in range(len(text) - self.n + 1):
            gram = text[i : i + self.n]
            context = gram[:-1]
            char    = gram[-1]
            self.counts[context][char] += 1
            self.vocab.add(char)

    def train_from_dir(self, clean_dir: str):
    
        for path in Path(clean_dir).glob("*.txt"):
            self.train(path.read_text(encoding="utf-8"))

    def log_prob(self, context: str, char: str) -> float:
    
        context_counts = self.counts[context]
        total = sum(context_counts.values()) + self.smoothing * (len(self.vocab) + 1)
        char_count = context_counts.get(char, 0) + self.smoothing
        return math.log(char_count / total)

    def score_text(self, text: str) -> float:
    
        if len(text) < self.n:
            return 0.0
        total = 0.0
        for i in range(len(text) - self.n + 1):
            gram    = text[i : i + self.n]
            context = gram[:-1]
            char    = gram[-1]
            total  += self.log_prob(context, char)
        return total

