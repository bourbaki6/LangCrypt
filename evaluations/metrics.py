

import math
from collections import Counter


def perplexity(log_likelihood, n_tokens):
    return math.exp(-log_likelihood / n_tokens)


def entropy(text):
    
    counts = Counter(text)
    total = sum(counts.values())

    ent = 0
    for c in counts.values():
        p = c / total
        ent -= p * math.log2(p)

    return ent

def average_log_likelihood(scores):
    return sum(scores) / len(scores)

