
import math
from collections import defaultdict
from pathlib import Path

from models.base_lm import BaseLanguageModel


class NGramModel(BaseLanguageModel):

    def __init__(self, n: int = 3, smoothing: float = 0.01):
        
        self.n = n
        self.smoothing = smoothing
      
        self.counts: dict = defaultdict(lambda: defaultdict(float))
        self.vocab: set = set()

    def train(self, text: str):
        
        text = text.lower()
        
        for i in range(len(text) - self.n + 1):
            gram = text[i : i + self.n]
            context = gram[:-1]  
            char = gram[-1]    
            self.counts[context][char] += 1
            self.vocab.add(char)

    def log_prob(self, context: str, char: str) -> float:
        
        V  = len(self.vocab) + 1           
        ctx_counts = self.counts[context]
        total = sum(ctx_counts.values()) + self.smoothing * V
        num  = ctx_counts.get(char, 0)  + self.smoothing
        
        return math.log(num / total)

    def score_text(self, text: str) -> float:
        
        text = text.lower()
        if len(text) < self.n:
            return 0.0
        total = 0.0
        for i in range(len(text) - self.n + 1):
            gram = text[i : i + self.n]
            context = gram[:-1]
            char = gram[-1]
            total += self.log_prob(context, char)
        return total

    def score(self, text: str) -> float:
       
        return self.score_text(text)

    def __repr__(self):
        return (f"NGramModel(n={self.n}, smoothing={self.smoothing}, "
                f"vocab_size={len(self.vocab)})")