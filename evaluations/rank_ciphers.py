

import os
from evaluation.evaluate import evaluate_model

def load_cipher_texts(folder):

    data = {}

    for file in os.listdir(folder):
        path = os.path.join(folder, file)

        with open(path, "r", encoding="utf-8") as f:
            data[file] = f.read()

    return data


def rank_ciphers(model, cipher_folder):

    texts = load_cipher_texts(cipher_folder)

    results = {}

    for name, text in texts.items():

        metrics = evaluate_model(model, text)

        results[name] = metrics

    ranked = sorted(
        results.items(),
        key = lambda x: x[1]["perplexity"],
        reverse = True
    )

    return ranked