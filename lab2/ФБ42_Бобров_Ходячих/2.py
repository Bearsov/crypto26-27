import os
import re
from collections import Counter

DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "var3.txt")

with open(DIR, "r", encoding="utf-8") as f:
    text = f.read()

ALPHABET = "абвгдежзийклмнопрстуфхцчшщъыьэюя"
M = len(ALPHABET)

CHAR_TO_IDX = {char: idx for idx, char in enumerate(ALPHABET)}
IDX_TO_CHAR = {idx: char for idx, char in enumerate(ALPHABET)}
ciphertext = [ch for ch in text.lower() if ch in CHAR_TO_IDX]
n = len(ciphertext)


def block_index_of_coincidence(block):
    length = len(block)
    if length <= 1:
        return 0.0
    counts = Counter(block)
    return sum(c * (c - 1) for c in counts.values()) / (length * (length - 1))


print(f"{'r':<4} | {'Ir':<10} | {'Dr':<14}")
print("-" * 40)

avg_ic_list = {}
dr_list = {}

for r in range(2, 31):
    blocks = [ciphertext[i::r] for i in range(r)]

    avg_ic = sum(block_index_of_coincidence(b) for b in blocks) / r
    avg_ic_list[r] = avg_ic

    d_r = sum(1 for i in range(n - r) if ciphertext[i] == ciphertext[i + r])
    dr_list[r] = d_r

    print(f"{r:<4} | {avg_ic:<10.6f} | {d_r:<14}")

print("\n" + "=" * 40)

top4 = sorted(avg_ic_list.items(), key=lambda item: item[1], reverse=True)[:4]

print("Найкращі кандидати (Ir>0.04):")
for r, ic in top4:
    print(f"r = {r:2d} | Ir = {ic:.6f}")
