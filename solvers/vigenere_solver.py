

import math
from collections import Counter
from typing import List, Optional, Tuple

from models.base_lm import BaseLanguageModel
from models.freq_model import FrequencyModel


ALPHABET = "abcdefghijklmnopqrstuvwxyz"


def _column_ic(text: str, key_len: int) -> float:
    
    letters = [c for c in text.lower() if c.isalpha()]
    columns = [letters[i::key_len] for i in range(key_len)]
    ics = [FrequencyModel.index_of_coincidence("".join(col))
                for col in columns if len(col) > 1]
    return sum(ics) / len(ics) if ics else 0.0


def estimate_key_length(ciphertext: str, max_len: int = 20, top_n: int = 3) -> List[int]:
   
    letters = [c for c in ciphertext.lower() if c.isalpha()]


    if len(letters) < 2 * max_len:
        max_len = max(2, len(letters) // 2)

    scores = []
    for length in range(2, max_len + 1):
        ic = _column_ic(ciphertext, length)
        scores.append((length, ic))

    scores.sort(key = lambda x: x[1], reverse = True)
    return [length for length, _ in scores[:top_n]]




def _find_column_shift(column_text: str) -> int:
    
    best_shift = 0
    best_chi2  = float("inf")

    for shift in range(26):
        
        decrypted = "".join(
            ALPHABET[(ALPHABET.index(c) - shift) % 26]
            for c in column_text.lower()
            if c.isalpha()
        )
        chi2 = FrequencyModel.chi_squared(decrypted)
        if chi2 < best_chi2:
            best_chi2  = chi2
            best_shift = shift

    return best_shift


def find_key(ciphertext: str, key_length: int) -> str:
    
    letters = [c for c in ciphertext.lower() if c.isalpha()]
    key = ""

    for col_idx in range(key_length):
        
        column = "".join(letters[col_idx::key_length])
        shift = _find_column_shift(column)
        key += ALPHABET[shift]

    return key




def _vigenere_decrypt(ciphertext: str, key: str) -> str:
   
    result   = []
    key_idx  = 0   

    for ch in ciphertext:
        if ch.isalpha():
            shift = ALPHABET.index(key[key_idx % len(key)])
            plain = ALPHABET[(ALPHABET.index(ch.lower()) - shift) % 26]
            result.append(plain)
            key_idx += 1
        else:
            result.append(ch)

    return "".join(result)



def _refine_key(ciphertext: str, initial_key: str, model: BaseLanguageModel, window: int = 2) -> Tuple[str, float]:
    
    key = list(initial_key)
    best_dec = _vigenere_decrypt(ciphertext, "".join(key))
    best_score = model.score_per_char(best_dec)

    improved = True
    while improved:
        improved = False
        for i in range(len(key)):
            current_shift = ALPHABET.index(key[i])
            
            for delta in range(-window, window + 1):
                
                if delta == 0:
                    continue
                
                candidate_key = key[:]
                candidate_key[i]  = ALPHABET[(current_shift + delta) % 26]
                decrypted = _vigenere_decrypt(ciphertext, "".join(candidate_key))
                score = model.score_per_char(decrypted)
                if score > best_score:
                    best_score  = score
                    key = candidate_key
                    improved = True  

    return "".join(key), best_score


def solve(ciphertext: str, model: BaseLanguageModel, max_key_len: int = 20, refine: bool = True) -> List[Tuple[str, float, str]]:
    

    key_lengths = estimate_key_length(ciphertext, max_len = max_key_len, top_n = 3)

    candidates = []
    for key_len in key_lengths:
        
        raw_key = find_key(ciphertext, key_len)

    
        if refine:
            key, score = _refine_key(ciphertext, raw_key, model)
        else:
            key = raw_key
            dec = _vigenere_decrypt(ciphertext, key)
            score = model.score_per_char(dec)

        decrypted = _vigenere_decrypt(ciphertext, key)
        candidates.append((key, score, decrypted))


    candidates.sort(key = lambda x: x[1], reverse = True)
    return candidates


def solve_best(ciphertext: str,  model: BaseLanguageModel,max_key_len: int = 20) -> Tuple[str, float, str]:
   
    return solve(ciphertext, model, max_key_len = max_key_len)[0]