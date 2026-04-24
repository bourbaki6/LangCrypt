

from models.n_gram import NGramModel
from evaluations.rank_ciphers import rank_ciphers

model = NGramModel(n = 3)

with open("data/clean/train.txt") as f:
    text = f.read()

model.train(text)

results = rank_ciphers(model, "data/ciphered")

for name, metrics in results:
    print(name, metrics)