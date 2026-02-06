from collections import defaultdict
import math

class CharNGramLM:

    def __init__(self, n=3):
        self.n = n
        self.counts = defaultdict(lambda: defaultdict(int))
        self.context_totals = defaultdict(int)
        self.vocab = set()

    def train(self, text: str):
        padded = "~" * (self.n - 1) + text
        for i in range(len(text)):
            context = padded[i:i + self.n - 1]
            char = text[i]
            self.counts[context][char] += 1
            self.context_totals[context] += 1
            self.vocab.add(char)

    def score(self, text: str):
        padded = "~" * (self.n - 1) + text
        log_prob = 0.0
        V = len(self.vocab)

        for i in range(len(text)):
            context = padded[i:i + self.n - 1]
            char = text[i]

            count = self.counts[context][char]
            total = self.context_totals[context]

            
            prob = (count + 1) / (total + V)
            log_prob += math.log(prob)

        return log_prob
