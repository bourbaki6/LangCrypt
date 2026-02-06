import math
from collections import defaultdict


class MarkovModel:
    
    def __init__(self, order=3):
        self.order = order
        self.counts = defaultdict(lambda: defaultdict(int))
        self.context_totals = defaultdict(int)
        self.vocab = set()


    def train(self, text):
        for i in range(len(text) - self.order):
            context = text[i:i+self.order]
            char = text[i+self.order]
            self.counts[context][char] += 1
            self.context_totals[context] += 1
            self.vocab.add(char)


    def log_prob(self, context, char, smoothing=1.0):
        vocab_size = len(self.vocab)
        count = self.counts[context][char]
        total = self.context_totals[context]
       
        return math.log((count + smoothing) / (total + smoothing * vocab_size))
