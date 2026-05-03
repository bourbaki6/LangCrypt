

import math
from abc import ABC, abstractmethod
from pathlib import Path


class BaseLanguageModel(ABC):

    def train(self, text: str):
        
        raise NotImplementedError(f"{self.__class__.__name__} does not implement train()")

    def train_from_dir(self, clean_dir: str):
        
        paths = sorted(Path(clean_dir).glob("*.txt"))
        if not paths:
            raise FileNotFoundError(f"No .txt files found in {clean_dir}")
        
        for path in paths:
            self.train(path.read_text(encoding = "utf-8"))


    @abstractmethod
    def score_text(self, text: str) -> float:
        ...

    def score_per_char(self, text: str) -> float:
        
        n = max(sum(1 for c in text if c.isalpha()), 1)
        return self.score_text(text) / n

    def perplexity(self, text: str) -> float:
        
        return math.exp(-self.score_per_char(text))

    def __repr__(self):
        return self.__class__.__name__