import os

DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "var3.txt")

with open(DIR, "r", encoding="utf-8") as f:
    text = f.read()

ALPHABET = "абвгдежзийклмнопрстуфхцчшщъыьэюя"
M = len(ALPHABET)

CHAR_TO_IDX = {char: idx for idx, char in enumerate(ALPHABET)}
IDX_TO_CHAR = {idx: char for idx, char in enumerate(ALPHABET)}
ciphertext = [ch for ch in text.lower() if ch in CHAR_TO_IDX]

key = "экомаятникфукн"
key_indices = [CHAR_TO_IDX[ch] for ch in key]
r = len(key_indices)

decrypted_text = "".join(
    IDX_TO_CHAR[(CHAR_TO_IDX[char] - key_indices[i % r]) % M]
    for i, char in enumerate(ciphertext)
)

print(decrypted_text[:500])