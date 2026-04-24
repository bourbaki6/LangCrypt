

import torch
import torch.nn as nn
import torch.nn.functional as F

class TransformerLanguageModel(nn.Module):

    def __init__(self, vocab_size, d_model=128):

        super().__init__()

        self.embed = nn.Embedding(vocab_size, d_model)

        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=4
        )

        self.transformer = nn.TransformerEncoder(
            encoder_layer,
            num_layers=4
        )

        self.fc = nn.Linear(d_model, vocab_size)

    def forward(self, x):

        x = self.embed(x)
        x = x.transpose(0,1)

        out = self.transformer(x)

        out = out.transpose(0,1)

        return self.fc(out)


class TransformerWrapper:

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