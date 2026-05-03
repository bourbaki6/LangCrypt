
import csv

from pathlib import Path
from typing import Dict, List, Optional, Tuple

from evaluations.evaluate import evaluate_model   
from models.base_lm import BaseLanguageModel


def load_cipher_texts(folder: str) -> Dict[str, str]:
   
    data = {}
    folder_path = Path(folder)
    if not folder_path.exists():
        raise FileNotFoundError(f"Cipher folder not found: {folder}")

    for filepath in sorted(folder_path.glob("*.txt")):
        try:
            data[filepath.name] = filepath.read_text(encoding="utf-8")
        except Exception as e:
            print(f"  Warning: could not read {filepath.name}: {e}")
    return data


def rank_ciphers(model: BaseLanguageModel,cipher_folder: str,verbose: bool = False) -> List[Tuple[str, Dict]]:
    
    texts   = load_cipher_texts(cipher_folder)
    results = {}

    for i, (name, text) in enumerate(texts.items()):
        if verbose and i % 50 == 0:
            print(f"  Scoring {i+1}/{len(texts)}: {name}")
        results[name] = evaluate_model(model, text)

    ranked = sorted(
        results.items(),
        key = lambda x: x[1]["log_likelihood_per_char"],
        reverse = True   
    )
    return ranked


def get_correct_rank(ranked_results: List[Tuple[str, Dict]],correct_filename: str) -> Optional[int]:
    
    for rank, (name, _) in enumerate(ranked_results, start = 1):
        if name == correct_filename:
            return rank
    
    return None


def to_csv(ranked_results: List[Tuple[str, Dict]],output_path: str) -> None:
    
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        
        writer.writerow([
            "rank", "filename",
            "log_likelihood_per_char", "perplexity",
            "entropy", "index_of_coincidence", "n_chars"
        ])
    
        for rank, (name, metrics) in enumerate(ranked_results, start=1):
            writer.writerow([
                rank,
                name,
                f"{metrics['log_likelihood_per_char']:.6f}",
                f"{metrics['perplexity']:.4f}",
                f"{metrics['entropy']:.4f}",
                f"{metrics['index_of_coincidence']:.6f}",
                int(metrics['n_chars']),
            ])
    print(f"Saved results to {output_path}")