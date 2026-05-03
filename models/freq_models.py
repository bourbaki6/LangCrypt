
#---unigram chrac freq model---#
#--- estimating P(char) from training text 
#    using freq counting with Laplace---#
#--- e = 12.7%, t = 9.1%, a = 8.2%, 
#    o = 7.5%, i = 7.0%, n = 6.7%---#



import math
from collections import Counter
from pathlib import Path

from models.base_lm import BaseLanguageModel


class FrequencyModel(BaseLanguageModel):
    
    ENGLISH_FREQ = {
        'a': 0.08167, 'b': 0.01492, 'c': 0.02782, 'd': 0.04253,
        'e': 0.12702, 'f': 0.02228, 'g': 0.02015, 'h': 0.06094,
        'i': 0.06966, 'j': 0.00153, 'k': 0.00772, 'l': 0.04025,
        'm': 0.02406, 'n': 0.06749, 'o': 0.07507, 'p': 0.01929,
        'q': 0.00095, 'r': 0.05987, 's': 0.06327, 't': 0.09056,
        'u': 0.02758, 'v': 0.00978, 'w': 0.02360, 'x': 0.00150,
        'y': 0.01974, 'z': 0.00074,
    }

    def __init__(self, smoothing: float = 0.5):
       
        self.smoothing = smoothing
        self.counts: Counter = Counter()
        self.total: int = 0


    def train(self, text: str):
       
        for ch in text.lower():           
            if ch.isalpha():
                self.counts[ch] += 1
                self.total += 1


    def log_prob(self, char: str) -> float:
        
        num = self.counts.get(char.lower(), 0) + self.smoothing
        den = self.total + self.smoothing * 26
        return math.log(num / den)

    def score_text(self, text: str) -> float:
        
        return sum(self.log_prob(ch) for ch in text.lower() if ch.isalpha())


    @classmethod
    def chi_squared(cls, text: str) -> float:
        
        letters = [c for c in text.lower() if c.isalpha()]
        n = len(letters)
        if n == 0:
            return float("inf")

        observed = Counter(letters)
        chi2 = 0.0
        for ch, expected_p in cls.ENGLISH_FREQ.items():
            expected = expected_p * n
            obs = observed.get(ch, 0)
            chi2 += (obs - expected) ** 2 / expected
        return chi2

    @staticmethod
    def index_of_coincidence(text: str) -> float:
       
        letters = [c for c in text.lower() if c.isalpha()]
        n = len(letters)
        if n < 2:
            return 0.0
        counts = Counter(letters)
        return sum(c * (c - 1) for c in counts.values()) / (n * (n - 1))

    def __repr__(self):
        return (f"FrequencyModel(smoothing={self.smoothing}, "
                f"trained_on={self.total:,}_chars)")