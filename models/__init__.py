

from models.base_lm import BaseLanguageModel
from models.freq_model import FrequencyModel
from models.ngram_model import NGramModel
from models.markov_model import MarkovModel


def load_gpt2():
    from models.gpt2_scorer import GPT2Scorer
    return GPT2Scorer()