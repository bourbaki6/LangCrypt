#---GPT-2 was trained on 40GB of English text (WebText corpus).  
#   366MB training corpus, while large enough for statistical models, 
#   produces an LM that is orders of magnitude less fluent than GPT-2---#


import math
from models.base_lm import BaseLanguageModel

_TRANSFORMERS_AVAILABLE = None


def _check_transformers():
    
    global _TRANSFORMERS_AVAILABLE
    if _TRANSFORMERS_AVAILABLE is None:
        try:
            import transformers  
            _TRANSFORMERS_AVAILABLE = True
        except ImportError:
            _TRANSFORMERS_AVAILABLE = False
    return _TRANSFORMERS_AVAILABLE


class GPT2Scorer(BaseLanguageModel):

    def __init__(self, device: str = "auto", max_chunk: int = 512):
        if not _check_transformers():
            raise ImportError(
                "transformers library not installed.\n"
                "Install with:  pip install transformers torch\n"
                "Then re-instantiate GPT2Scorer()."
            )

        import torch
        from transformers import GPT2LMHeadModel, GPT2TokenizerFast

        if device == "auto":
            self._device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self._device = device

        self.max_chunk = max_chunk

        print(f"[GPT2Scorer] Loading GPT-2 small on {self._device}...")
        
        self._tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")
        self._model = GPT2LMHeadModel.from_pretrained("gpt2")
        self._model.eval()
        self._model.to(self._device)
        
        print("[GPT2Scorer] Ready.")

    def train(self, text: str):
      
        pass

    def score_text(self, text: str) -> float:
       
        import torch

        encodings = self._tokenizer(text, return_tensors="pt")
        input_ids = encodings.input_ids.to(self._device)
        n_tokens  = input_ids.size(1)

        if n_tokens == 0:
            return 0.0

        total_log_prob = 0.0
        n_scored = 0

        stride = self.max_chunk // 2  
        chunk_size = self.max_chunk

        with torch.no_grad():
            for begin in range(0, n_tokens, stride):
                end = min(begin + chunk_size, n_tokens)
                chunk = input_ids[:, begin:end]

                if chunk.size(1) < 2:
                    break

                outputs  = self._model(chunk, labels=chunk)
                chunk_len = chunk.size(1) - 1   
                total_log_prob -= outputs.loss.item() * chunk_len
                n_scored += chunk_len

                if end == n_tokens:
                    break

        return total_log_prob

    def score(self, text: str) -> float:
    
        return self.score_text(text)

    def __repr__(self):
        return f"GPT2Scorer(device={self._device})"