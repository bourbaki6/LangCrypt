
import math
from collections import Counter
from pathlib import Path
from typing import Dict

from models.base_lm import BaseLanguageModel
from models.freq_model import FrequencyModel   


def evaluate_model(model: BaseLanguageModel, text: str) -> Dict[str, float]:

    from evaluations.metrics import perplexity, entropy  

    log_likelihood = model.score_text(text)

    n_chars = max(sum(1 for c in text if c.isalpha()), 1)

    ll_per_char = log_likelihood / n_chars

    ppl = math.exp(-ll_per_char)  

    ent = entropy(text)

    ic = FrequencyModel.index_of_coincidence(text)

    return {
        "log_likelihood": log_likelihood,
        "log_likelihood_per_char": ll_per_char,
        "perplexity": ppl,
        "entropy": ent,
        "index_of_coincidence": ic,
        "n_chars": n_chars,
    }


def evaluate_file(model: BaseLanguageModel,filepath: str) -> Dict[str, float]:
    
    text = Path(filepath).read_text(encoding = "utf-8")
    return evaluate_model(model, text)


def evaluate_directory(model: BaseLanguageModel,directory: str) -> Dict[str, Dict[str, float]]:
    
    results = {}
    for path in sorted(Path(directory).glob("*.txt")):
        results[path.name] = evaluate_file(model, str(path))
    return results