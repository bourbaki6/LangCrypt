"""

perplexity(log_likelihood, n_tokens):
    The standard language modelling metric.
    Lower = the model is less "surprised" by the text = more English-like.
    English prose typically gives perplexity 3-10 on a trigram model.
    Ciphered text typically gives perplexity 20-26 (close to uniform = 26).

entropy(text):
    Shannon entropy of the character distribution in the text.
    Measured in bits.
    English text: ~4.0-4.5 bits (non-uniform distribution).
    Vigenère with long key: ~4.7 bits (more uniform).
    AES/DES output: ~4.7 bits (statistically random).
    Used as a FAST cipher-type diagnostic — doesn't require a trained model.

average_log_likelihood(scores):
    Mean of a list of per-text scores.
    Used when aggregating results across multiple files.
"""

import math
from collections import Counter


def perplexity(log_likelihood: float, n_tokens: int) -> float:
  
    if n_tokens <= 0:
        return float("inf")
    
    avg_nll = -log_likelihood / n_tokens
    
    return math.exp(min(avg_nll, 20.0))


def entropy(text: str) -> float:
    
    letters = [c for c in text.lower() if c.isalpha()]
    total = len(letters)
    if total == 0:
        return 0.0

    counts = Counter(letters)
    ent = 0.0
    for count in counts.values():
        p = count / total
        ent -= p * math.log2(p)
    return ent


def average_log_likelihood(scores: list) -> float:
  
    if not scores:
        return 0.0
    return sum(scores) / len(scores)
