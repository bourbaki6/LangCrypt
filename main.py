

import argparse
import csv
import sys
import time
from pathlib import Path


sys.path.insert(0, str(Path(__file__).parent))

from models.freq_model  import FrequencyModel
from models.ngram_model import NGramModel
from models.markov_model import MarkovModel
from evaluations.evaluate import evaluate_model


CLEAN_DIR = Path("data/clean_text")
RESULTS_DIR  = Path("results")


VIGENERE_KEYS = ["cipher", "language", "secret", "model", "neural"]

ALPHABET = "abcdefghijklmnopqrstuvwxyz"


def caesar_decrypt(text: str, shift: int) -> str:
    
    result = []
    for ch in text.lower():
        if ch.isalpha():
            result.append(ALPHABET[(ALPHABET.index(ch) - shift) % 26])
        else:
            result.append(ch)
    return "".join(result)


def vigenere_decrypt(text: str, key: str) -> str:
    
    result  = []
    key_idx = 0
    for ch in text.lower():
        if ch.isalpha():
            shift = ALPHABET.index(key[key_idx % len(key)])
            result.append(ALPHABET[(ALPHABET.index(ch) - shift) % 26])
            key_idx += 1
        else:
            result.append(ch)
    return "".join(result)



def run_caesar_experiment(model,model_name: str,  texts_dir: Path, quick: bool = False) -> list:
    
    results = []
    text_files = sorted(texts_dir.glob("*.txt"))
    if quick:
        text_files = text_files[:10]

    for text_file in text_files:
        plaintext = text_file.read_text(encoding="utf-8").lower()
        topic = text_file.stem

        for true_shift in range(1, 26):
            
            ciphertext = "".join(
                ALPHABET[(ALPHABET.index(c) + true_shift) % 26]
                if c.isalpha() else c
                for c in plaintext
            )


            scores = []
            for candidate_shift in range(1, 26):
                dec = caesar_decrypt(ciphertext, candidate_shift)
                score = model.score_per_char(dec)
                scores.append((candidate_shift, score))

            scores.sort(key=lambda x: x[1], reverse=True)
            ranked_shifts = [s for s, _ in scores]
            correct_rank  = ranked_shifts.index(true_shift) + 1  # 1-based

            results.append({
                "model": model_name,
                "cipher": "caesar",
                "topic": topic,
                "true_key": str(true_shift),
                "predicted_key": str(ranked_shifts[0]),
                "correct_rank": correct_rank,
                "correct": correct_rank == 1,
                "top1_score":    round(scores[0][1], 6),
            })

    return results



def run_vigenere_experiment(model,model_name: str,texts_dir: Path, quick: bool = False) -> list:
    
    results = []
    text_files = sorted(texts_dir.glob("*.txt"))
    if quick:
        text_files = text_files[:5]

    for text_file in text_files:
        plaintext = text_file.read_text(encoding = "utf-8").lower()
        topic = text_file.stem

        for true_key in VIGENERE_KEYS:
            
            ciphertext = []
            key_idx = 0
            for ch in plaintext:
                if ch.isalpha():
                    shift = ALPHABET.index(true_key[key_idx % len(true_key)])
                    ciphertext.append(ALPHABET[(ALPHABET.index(ch) + shift) % 26])
                    key_idx += 1
                else:
                    ciphertext.append(ch)
            ciphertext = "".join(ciphertext)

          
            scores = []
            for candidate_key in VIGENERE_KEYS:
                dec = vigenere_decrypt(ciphertext, candidate_key)
                score = model.score_per_char(dec)
                scores.append((candidate_key, score))

            scores.sort(key=lambda x: x[1], reverse=True)
            ranked_keys = [k for k, _ in scores]
            correct_rank = ranked_keys.index(true_key) + 1

            results.append({
                "model": model_name,
                "cipher": "vigenere",
                "topic":topic,
                "true_key": true_key,
                "predicted_key": ranked_keys[0],
                "correct_rank":  correct_rank,
                "correct": correct_rank == 1,
                "top1_score":    round(scores[0][1], 6),
            })

    return results



def save_results(all_results: list, output_path: Path):
    
    if not all_results:
        print("No results to save.")
        return
   
    RESULTS_DIR.mkdir(exist_ok=True)
    fieldnames = list(all_results[0].keys())
    
    with open(output_path, "w", newline = "", encoding = "utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_results)
    print(f"\nSaved {len(all_results):,} results to {output_path}")


def print_summary(all_results: list):
    
    from collections import defaultdict
    summary = defaultdict(lambda: {"correct": 0, "total": 0})
    
    for r in all_results:
        key = (r["model"], r["cipher"])
        summary[key]["total"] += 1
        summary[key]["correct"] += int(r["correct"])


    print(f"{'Model':<26} {'Cipher':<12} {'Accuracy':>10} {'N':>6}")
  
    for (model, cipher), counts in sorted(summary.items()):
        acc = counts["correct"] / counts["total"] * 100
        print(f"{model:<26} {cipher:<12} {acc:>9.1f}% {counts['total']:>6}")
   


def main():
    parser = argparse.ArgumentParser(
        description = "LangCrypt — cipher breaking with language models"
    )
    
    parser.add_argument("--quick",
                        action = "store_true",
                        help = "Quick mode: 10 texts for Caesar, 5 for Vigenère")
    parser.add_argument("--transformer",
                        default = None,
                        metavar = "CHECKPOINT",
                        help = "Path to trained transformer checkpoint (.pt file). "
                             "Train first with: python train_models.py")
    parser.add_argument("--gpt2",
                        action = "store_true",
                        help = "Include GPT-2 scorer (requires: pip install transformers torch)")
    args = parser.parse_args()

    if not CLEAN_DIR.exists():
        print(f"ERROR: Clean text directory not found: {CLEAN_DIR}")
      
        sys.exit(1)


    print("\n LangCrypt")
  
    models = {}

    print("\n[1/3] Training FrequencyModel")
    t0 = time.time()
    freq_model = FrequencyModel(smoothing = 0.5)
    freq_model.train_from_dir(str(CLEAN_DIR))
    
    print(f" {time.time()-t0:.1f}s  |  {freq_model}")
    models["FrequencyModel"] = freq_model

    print("\n[2/3] Training NGramModel (n = 3)")
    
    t0 = time.time()
    ngram_model = NGramModel(n = 3, smoothing =  0.01)
    ngram_model.train_from_dir(str(CLEAN_DIR))
    
    print(f" {time.time()-t0:.1f}s  |  {ngram_model}")
    models["NGramModel_n3"] = ngram_model

    print("\n[3/3] Training MarkovModel (order = 4)")
    t0 = time.time()
    markov_model = MarkovModel(order = 4, smoothing = 1.0)
    markov_model.train_from_dir(str(CLEAN_DIR))
    
    print(f" {time.time()-t0:.1f}s  |  {markov_model}")
    models["MarkovModel_o4"] = markov_model


    if args.transformer:
        ckpt = Path(args.transformer)
        if not ckpt.exists():
            print(f"\nWARNING: Transformer checkpoint not found: {ckpt}")
            print("\n Train ")
            print("\n Skipping transformer.")
        else:
            print(f"\n[+] Loading Transformer from {ckpt}")
            try:
                
                from models.transformer_lm import TransformerLanguageModel
                
                t_model = TransformerLanguageModel(device = "auto")
                t_model.load(str(ckpt))
                models["Transformer"] = t_model
                print(f" {t_model}")
            except Exception as e:
                print(f"    WARNING: Could not load transformer: {e}")

    if args.gpt2:
        print("\n[+] Loading GPT-2 scorer (pretrained, no training needed)...")
        try:
            
            from models.gpt2_scorer import GPT2Scorer
            
            gpt2_model  = GPT2Scorer(device = "auto")
            models["GPT2"] = gpt2_model
        
        except ImportError as e:
            print(f" WARNING: Could not load GPT-2: {e}")

    all_results = []
    n_models = len(models)

    for m_idx, (model_name, model) in enumerate(models.items(), 1):
        print(f"\n[{m_idx}/{n_models}] {model_name} — Caesar experiment")
        t0 = time.time()
        caesar_results = run_caesar_experiment(
            model, model_name, CLEAN_DIR, quick = args.quick
        )
        all_results.extend(caesar_results)
        n_correct = sum(r["correct"] for r in caesar_results)
        acc = n_correct / len(caesar_results) * 100
        print(f"  Caesar:   {acc:6.1f}%  ({n_correct}/{len(caesar_results)})  "
              f"{time.time()-t0:.1f}s")

        print(f" {model_name} — Vigenère experiment")
        t0 = time.time()
        vig_results = run_vigenere_experiment(
            model, model_name, CLEAN_DIR, quick=args.quick
        )
        all_results.extend(vig_results)
        n_correct = sum(r["correct"] for r in vig_results)
        acc = n_correct / len(vig_results) * 100
        print(f" Vigenère: {acc:6.1f}%  ({n_correct}/{len(vig_results)})  "
              f"{time.time()-t0:.1f}s")


    output_path = RESULTS_DIR / "results.csv"
    save_results(all_results, output_path)
    print_summary(all_results)

    print(f"\nDone. Saved to {output_path}")


if __name__ == "__main__":
    main()