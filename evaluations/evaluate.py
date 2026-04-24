

import os
from evaluations.metrics imort perplexity, entropy

def evaluate_model(model, text):

    log_likelihood = model.score(text)
    n_tokens = len(text)

    ppl = perplexity(log_likelihood, n_tokens)
    ent= entropy(text)

    return {
        "log_likelihood": log_likelihood,
        "perplexity": ppl,
        "entropy": ent
    }