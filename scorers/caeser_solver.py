
from typing import List, Tuple

from models.base_lm import BaseLanguageModel
from models.freq_model import FrequencyModel

ALPHABET = "abcdefghijklmnopqrstuvwxyz"


def _caesar_decrypt(text: str, shift: int) -> str:
    
    result = []
    for ch in text:
        
        if ch.isalpha():
            result.append(ALPHABET[(ALPHABET.index(ch.lower()) - shift) % 26])
        
        else:
            result.append(ch)   
    return "".join(result)


def solve(ciphertext: str,model: BaseLanguageModel,top_n: int = 5) -> List[Tuple[int, float, str]]:
  
    results = []

    for shift in range(1, 26):
        
        decrypted = _caesar_decrypt(ciphertext, shift)

        score = model.score_per_char(decrypted)

        results.append((shift, score, decrypted))

    results.sort(key = lambda x: x[1], reverse = True)

    return results[:top_n]


def solve_chi_squared(ciphertext: str) -> List[Tuple[int, float, str]]:
    
    results = []
    for shift in range(1, 26):
        decrypted = _caesar_decrypt(ciphertext, shift)
        chi2 = FrequencyModel.chi_squared(decrypted)
        results.append((shift, chi2, decrypted))

    results.sort(key=lambda x: x[1])

    return results


def solve_best(ciphertext: str, model: BaseLanguageModel) -> Tuple[int, float, str]:
    
    return solve(ciphertext, model, top_n = 1)[0]