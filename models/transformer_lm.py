
import math
from pathlib import Path
from typing import Optional

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, Dataset

from models.base_lm import BaseLanguageModel



class CharVocab:
    
    PAD = 0

    def __init__(self):
        self.ch2i: dict = {"<PAD>": self.PAD}
        self.i2ch: list = ["<PAD>"]

    def build(self, text: str):
        
        for ch in sorted(set(text)):
            if ch not in self.ch2i:
                self.ch2i[ch] = len(self.i2ch)
                self.i2ch.append(ch)

    def encode(self, text: str) -> list:
        
        return [self.ch2i.get(ch, self.PAD) for ch in text]

    def decode(self, indices: list) -> str:
        
        return "".join(self.i2ch[i] for i in indices if i != self.PAD)

    def __len__(self):
        return len(self.i2ch)


class CharDataset(Dataset):
    

    def __init__(self, text: str, vocab: CharVocab,
                 seq_len: int = 256, stride: Optional[int] = None):
        
        if stride is None:
            stride = seq_len
        ids = vocab.encode(text)
        self.pairs = []
        
        for i in range(0, len(ids) - seq_len, stride):
            x = torch.tensor(ids[i:i + seq_len], dtype = torch.long)
            y = torch.tensor(ids[i + 1 : i + seq_len + 1], dtype = torch.long)
            self.pairs.append((x, y))

    def __len__(self):
        return len(self.pairs)

    def __getitem__(self, idx):
        return self.pairs[idx]


class SinusoidalPositionalEncoding(nn.Module):


    def __init__(self, d_model: int, max_len: int = 2048, dropout: float = 0.1):
        super().__init__()
        self.dropout = nn.Dropout(p = dropout)

        # Compute positional encodings once at construction time
        pe  = torch.zeros(max_len, d_model)
        pos = torch.arange(0, max_len, dtype = torch.float).unsqueeze(1)
     
        div = torch.exp(
            torch.arange(0, d_model, 2, dtype = torch.float)
            * (-math.log(10000.0) / d_model)
        )
        pe[:, 0::2] = torch.sin(pos * div)  
        pe[:, 1::2] = torch.cos(pos * div) 

        self.register_buffer("pe", pe.unsqueeze(0))  

    def forward(self, x: torch.Tensor) -> torch.Tensor:
       
        x = x + self.pe[:, : x.size(1)]
        return self.dropout(x)

class _TransformerCore(nn.Module):
    

    def __init__(self, vocab_size: int, d_model: int = 128,
                 nhead: int = 4, num_layers: int = 4,
                 dim_ff: int = 512, dropout: float = 0.1,
                 max_seq_len: int = 512):
       
        super().__init__()

        self.d_model = d_model
        self.embed   = nn.Embedding(vocab_size, d_model, padding_idx = CharVocab.PAD)
        self.pos_enc = SinusoidalPositionalEncoding(d_model, max_seq_len, dropout)
        decoder_layer = nn.TransformerDecoderLayer(
            d_model = d_model,
            nhead = nhead,
            dim_feedforward = dim_ff,
            dropout = dropout,
            batch_first = True,    
            norm_first = True,     
        )
        self.transformer = nn.TransformerDecoder(decoder_layer,
                                                  num_layers = num_layers)
        self.fc = nn.Linear(d_model, vocab_size)
        self.fc.weight = self.embed.weight
        self._init_weights()

    def _init_weights(self):
    
        for p in self.parameters():
            if p.dim() > 1:
                nn.init.xavier_uniform_(p)

    def _causal_mask(self, sz: int, device: torch.device) -> torch.Tensor:
    
        return torch.triu(
            torch.ones(sz, sz, device = device, dtype= torch.bool), diagonal = 1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        
        T = x.size(1)
        mask = self._causal_mask(T, x.device)

        emb = self.pos_enc(self.embed(x) * math.sqrt(self.d_model))

        out = self.transformer(emb, emb, tgt_mask = mask, memory_mask = mask,
                                  tgt_is_causal = True, memory_is_causal = True)

    
        return self.fc(out)


class TransformerLanguageModel(BaseLanguageModel):
    

    def __init__(self, d_model: int = 128, nhead: int = 4,
                 num_layers: int = 4, dim_ff: int = 512,
                 dropout: float = 0.1, seq_len: int = 256,
                 device: str = "auto"):
       
        self.d_model  = d_model
        self.nhead = nhead
        self.num_layers = num_layers
        self.dim_ff = dim_ff
        self.dropout = dropout
        self.seq_len  = seq_len

        
        if device == "auto":
            self._device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self._device = torch.device(device)

        self.vocab = CharVocab()
        self._model: Optional[_TransformerCore] = None

   

    def train(self, text: str, epochs: int = 10, batch_size: int = 32,
              lr: float = 3e-4, warmup_steps: int = 1000,
              print_every: int = 1, stride: Optional[int] = None):
        
        if len(self.vocab) == 1:   
            self.vocab.build(text)

        if self._model is None:
            self._build_model()

        dataset = CharDataset(text, self.vocab, self.seq_len, stride)
        if len(dataset) == 0:
            print(f"  [Transformer] WARNING: text too short for seq_len={self.seq_len}")
            return
        loader = DataLoader(dataset, batch_size = batch_size,
                            shuffle=True, pin_memory = (self._device.type == "cuda"))

    
        optimizer = torch.optim.AdamW(
            self._model.parameters(), lr = lr, weight_decay = 0.01
        )

        total_steps = epochs * len(loader)
        def lr_lambda(step):
            if step < warmup_steps:
                return step / max(warmup_steps, 1)
            progress = (step - warmup_steps) / max(total_steps - warmup_steps, 1)
            return max(0.1, 0.5 * (1 + math.cos(math.pi * progress)))

        scheduler = torch.optim.lr_scheduler.LambdaLR(optimizer, lr_lambda)
        criterion = nn.CrossEntropyLoss(ignore_index=CharVocab.PAD)
        step_count = 0

        self._model.train()
        for epoch in range(1, epochs + 1):
            total_loss = 0.0
            n_batches  = 0

            for x, y in loader:
                x = x.to(self._device)
                y = y.to(self._device)

                optimizer.zero_grad()
                logits = self._model(x)

                loss = criterion(
                    logits.reshape(-1, len(self.vocab)),
                    y.reshape(-1)
                )

                loss.backward()

                nn.utils.clip_grad_norm_(self._model.parameters(), max_norm = 1.0)

                optimizer.step()
                scheduler.step()
                step_count += 1

                total_loss += loss.item()
                n_batches += 1

            if epoch % print_every == 0 or epoch == epochs:
                avg_loss = total_loss / max(n_batches, 1)
                ppl = math.exp(min(avg_loss, 20))
                lr_now   = scheduler.get_last_lr()[0]
                print(f"  [Transformer] epoch {epoch:3d}/{epochs}"
                      f"  loss={avg_loss:.4f}  ppl={ppl:.1f}"
                      f"  lr={lr_now:.2e}"
                      f"  device={self._device}")

    def train_from_dir(self, clean_dir: str, **train_kwargs):
        
        print(f"[Transformer] Loading corpus from {clean_dir}")
        paths = sorted(Path(clean_dir).glob("*.txt"))
        if not paths:
            raise FileNotFoundError(f"No .txt files in {clean_dir}")

        all_text = ""
        for path in paths:
            all_text += path.read_text(encoding="utf-8")

        n_chars = len(all_text)
        print(f"[Transformer] Corpus: {n_chars:,} chars from {len(paths)} files")

        self.vocab.build(all_text)
        print(f"[Transformer] Vocabulary: {len(self.vocab)} unique characters")

        self._build_model()
        n_params = sum(p.numel() for p in self._model.parameters())
        print(f"[Transformer] Model: {n_params:,} parameters on {self._device}")

        self.train(all_text, **train_kwargs)

    def _build_model(self):
        
        self._model = _TransformerCore(
            vocab_size  = len(self.vocab),
            d_model = self.d_model,
            nhead = self.nhead,
            num_layers  = self.num_layers,
            dim_ff = self.dim_ff,
            dropout = self.dropout,
            max_seq_len = self.seq_len + 64,  
        ).to(self._device)

    def score_text(self, text: str) -> float:
        
        if self._model is None:
            raise RuntimeError(
                
            )
        self._model.eval()

        ids = self.vocab.encode(text)
        n  = len(ids)
        if n < 2:
            return 0.0

        total_log_prob = 0.0

        with torch.no_grad():
            for start in range(0, n - 1, self.seq_len):
            
                end = min(start + self.seq_len, n - 1)
                chunk_x = torch.tensor(
                    ids[start : end], dtype=torch.long
                ).unsqueeze(0).to(self._device)             # (1, T)

        
                targets = ids[start + 1 : end + 1]

                logits = self._model(chunk_x)           
                log_probs = F.log_softmax(logits[0], dim= -1) 

                for t, target_idx in enumerate(targets):
                    if t < log_probs.size(0):
                        total_log_prob += log_probs[t, target_idx].item()

        return total_log_prob

    def score(self, text: str) -> float:
        
        return self.score_text(text)

    def save(self, path: str):
       
        Path(path).parent.mkdir(parents = True, exist_ok = True)
        torch.save({
            "vocab": self.vocab,
            "state": self._model.state_dict(),
            "config": {
                "d_model": self.d_model,
                "nhead":  self.nhead,
                "num_layers": self.num_layers,
                "dim_ff": self.dim_ff,
                "dropout": self.dropout,
                "seq_len": self.seq_len,
            }
        }, path)
        n_params = sum(p.numel() for p in self._model.parameters())
        print(f"[Transformer] Saved to {path}  ({n_params:,} params)")

    def load(self, path: str):
        
        ckpt = torch.load(path, map_location = self._device)
        self.vocab = ckpt["vocab"]
        cfg = ckpt["config"]

        self.d_model = cfg["d_model"]
        self.nhead = cfg["nhead"]
        self.num_layers = cfg["num_layers"]
        self.dim_ff = cfg["dim_ff"]
        self.dropout = cfg["dropout"]
        self.seq_len = cfg["seq_len"]

        self._build_model()
        self._model.load_state_dict(ckpt["state"])
        self._model.eval()

        n_params = sum(p.numel() for p in self._model.parameters())
        print(f"[Transformer] Loaded from {path}  ({n_params:,} params)")

    def __repr__(self):
        return (f"TransformerLanguageModel("
                f"d_model={self.d_model}, "
                f"nhead={self.nhead}, "
                f"layers={self.num_layers}, "
                f"device={self._device})")