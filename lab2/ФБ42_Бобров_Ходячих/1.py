import os
import re
from collections import Counter

DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "war.txt")

with open(DIR, "r", encoding="utf-8") as f:
    text = f.read()

ALPHABET = "абвгдежзийклмнопрстуфхцчшщъыьэюя"
M = len(ALPHABET)

CHAR_TO_IDX = {char: idx for idx, char in enumerate(ALPHABET)}
IDX_TO_CHAR = {idx: char for idx, char in enumerate(ALPHABET)}

def calc_index(t):
    n = len(t)
    counts = Counter(t)
    return sum(count * (count - 1) for count in counts.values()) / (
        n * (n - 1)
    )


def vig_encrypt(plain_text, key_indices):
    r = len(key_indices)
    ciphertext_chars = []
    for i, char in enumerate(plain_text):
        x_i = CHAR_TO_IDX[char]
        k_i = key_indices[i % r]
        y_i = (x_i + k_i) % M
        ciphertext_chars.append(IDX_TO_CHAR[y_i])
    return "".join(ciphertext_chars)

print(f"Довжина відкритого тексту: {len(text)}")
print(f"Індекс відповідності ВТ: {calc_index(text):.6f}\n")

periods = [2, 3, 4, 5, 17, 100]

for r in periods:
    key_indices = [i % M for i in range(r)]
    ciphertext = vig_encrypt(text, key_indices)
    i_cipher = calc_index(ciphertext)
    print(f"r = {r:2d} | Індекс відповідності ШТ: {i_cipher:.6f}")