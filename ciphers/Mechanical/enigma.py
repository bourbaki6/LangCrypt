from pathlib import Path

CLEAN_DIR = Path("data/clean_text")
OUT_DIR = Path("data/ciphered_text/enigma")
OUT_DIR.mkdir(parents=True, exist_ok=True)

ALPHABET = "abcdefghijklmnopqrstuvwxyz"

ROTORS = {
    "I": ("ekmflgdqvzntowyhxuspaibrcj", "q"),  
    "II": ("ajdksiruxblhwtmcqgznpyfvoe", "e"),
    "III": ("bdfhjlcprtxvznyeiwgakmusqo", "v"),
}
REFLECTOR_B = "yruhqsldpxngokmiebfzcwvjat"

class Rotor:
    def __init__(self, wiring, notch, ring=0, start='a'):
        self.wiring = wiring
        self.notch = notch
        self.ring = ring
        self.pos = ALPHABET.index(start)

    def step(self):
        self.pos = (self.pos + 1) % 26

    def at_notch(self):
        return ALPHABET[self.pos] == self.notch

    def forward(self, c):
        idx = (ALPHABET.index(c) + self.pos - self.ring) % 26
        out = self.wiring[idx]
        return ALPHABET[(ALPHABET.index(out) - self.pos + self.ring) % 26]

    def backward(self, c):
        idx = (ALPHABET.index(c) + self.pos - self.ring) % 26
        out_idx = self.wiring.index(ALPHABET[idx])
        return ALPHABET[(out_idx - self.pos + self.ring) % 26]

def make_plugboard(pairs):
    board = dict(zip(ALPHABET, ALPHABET))
    for a, b in pairs:
        board[a] = b
        board[b] = a
    return board

def encrypt_char(c, rotors, reflector, plugboard):

    c = plugboard[c]
    
    if rotors[1].at_notch():
        rotors[1].step()
        rotors[0].step()
    elif rotors[2].at_notch():
        rotors[1].step()
    rotors[2].step()
    
    for r in reversed(rotors):
        c = r.forward(c)

    c = reflector[ALPHABET.index(c)]

    for r in rotors:
        c = r.backward(c)

    return plugboard[c]

def encrypt(text, rotor_names=("I", "II", "III"), starts=('a','a','a'),
            plugboard_pairs=None):
    r = [Rotor(*ROTORS[n], start=s) for n, s in zip(rotor_names, starts)]
    pb = make_plugboard(plugboard_pairs or [])
    result = []
    for c in text:
        if c in ALPHABET:
            result.append(encrypt_char(c, r, REFLECTOR_B, pb))
        else:
            result.append(c)
    return ''.join(result)

decrypt = encrypt

CONFIGS = [
    {"rotor_names": ("I",  "II",  "III"), "starts": ('a','a','a'), "plugboard_pairs": []},
    {"rotor_names": ("I",  "III", "II"),  "starts": ('a','b','c'), "plugboard_pairs": [('a','b'),('c','d')]},
    {"rotor_names": ("II", "I",   "III"), "starts": ('x','y','z'), "plugboard_pairs": [('e','f'),('g','h')]},
]

for file in CLEAN_DIR.glob("*.txt"):
    text = file.read_text(encoding="utf-8")
    for idx, cfg in enumerate(CONFIGS):
        cipher = encrypt(text, **cfg)
        out_name = f"{file.stem}_enigma_{idx}.txt"
        (OUT_DIR / out_name).write_text(cipher, encoding="utf-8")
        print("Saved:", out_name)