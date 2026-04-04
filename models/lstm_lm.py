
import torch
import torch.nn as nn
import torch.nn.functional as F

class LSTMLanguageModel(nn.Module):

    def __init__(self, vocab_size, hidden=128):

        super().__init__()

        self.embed = nn.Embedding(vocab_size, hidden)

        self.lstm = nn.LSTM(
            hidden,
            hidden,
            num_layers=2,
            batch_first=True
        )

        self.fc = nn.Linear(hidden, vocab_size)

    def forward(self, x):

        x = self.embed(x)
        out, _ = self.lstm(x)
        logits = self.fc(out)

        return logits


class LSTMWrapper:

    def __init__(self, model, vocab):

        self.model = model
        self.vocab = vocab

    def encode(self, text):
        return torch.tensor(
            [self.vocab[c] for c in text if c in self.vocab]
        ).unsqueeze(0)

    def score(self, text):

        self.model.eval()

        x = self.encode(text)

        with torch.no_grad():

            logits = self.model(x)

            log_probs = F.log_softmax(logits, dim=-1)

            score = 0

            for i in range(x.size(1) - 1):
                token = x[0, i+1]
                score += log_probs[0, i, token]

        return score.item()