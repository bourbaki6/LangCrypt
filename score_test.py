import math

def score_text(text, model):
    
    order = model.order
    log_likelihood = 0.0
    n = 0

    for i in range(len(text) - order):
        context = text[i:i+order]
        char = text[i+order]
        log_likelihood += model.log_prob(context, char)
        n += 1

    if n == 0:
        return -math.inf

    return log_likelihood / n
