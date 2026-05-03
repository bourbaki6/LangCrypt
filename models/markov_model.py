
import math
from collections import defaultdict
from pathlib import Path

from models.base_lm import BaseLanguageModel


class MarkovModel(BaseLanguageModel):


    def __init__(self, order: int = 4, smoothing: float = 1.0):
        
        self.order = order
        self.smoothing = smoothing
        self.counts: list = [
            defaultdict(lambda: defaultdict(float))
            for _ in range(order + 1)
        ]
        self.vocab: set = set()

    def train(self, text: str):
       
        text = text.lower()
        for i in range(len(text)):
            char = text[i]
            self.vocab.add(char)
        
            for k in range(min(self.order, i) + 1):     
                context = text[i - k : i]  
                self.counts[k][context][char] += 1



    def log_prob(self, context: str, char: str) -> float:
        
        V = len(self.vocab) + 1  

    
        for k in range(len(context), -1, -1):
            ctx  = context[-k:] if k > 0 else ""
            ctx_table = self.counts[k][ctx]
            total = sum(ctx_table.values())

            if total > 0:
                num = ctx_table.get(char, 0) + self.smoothing
                den = total + self.smoothing * V
                return math.log(num / den)

        return math.log(1.0 / max(V, 1))

    def score_text(self, text: str) -> float:
       
        text  = text.lower()
        score = 0.0
        for i in range(len(text)):
            char = text[i]
            context = text[max(0, i - self.order) : i]
            score += self.log_prob(context, char)
        return score

    def score(self, text: str) -> float:
    
        return self.score_text(text)

    def __repr__(self):
        return (f"MarkovModel(order={self.order}, "
                f"vocab_size={len(self.vocab)})")