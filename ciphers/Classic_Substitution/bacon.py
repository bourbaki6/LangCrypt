#---original binary cipher with a = 0, b = 1---#

from pathlib import Path

CLEAN_DIR = Path("data/clean_text")
OUT_DIR = Path("data/ciphered_text/bacon")
OUT_DIR.mkdir(parents=True, exist_ok=True)

code = {'A: aaaa', 'B: aaab', 'C: aaaba', 'D: aaabb',
        'E: aabaa', 'F: aabab', 'G: aabba', 'H: aabbb',
        'I: abaaa', 'J: abaab', 'K: ababa', 'L: ababb',
        'M: abbaa', 'N: abbab', 'O: abbba', 'P: abbbb',
        'Q: baaaa', 'R: baaab', 'S: baaba', 'T: baabb',
        'U: babaa', 'V: babab', 'W: babba', 'X: babbb',
        'Y: bbaaa', 'Z: bbaab'}

