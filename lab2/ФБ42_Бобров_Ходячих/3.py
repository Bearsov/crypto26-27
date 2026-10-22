import os
import re
from collections import Counter

DIr = os.path.join(os.path.dirname(os.path.abspath(__file__)), "var3.txt")

with open(DIr, "r", encoding="utf-8") as f:
    text = f.read()

ALPHABET = "абвгдежзийклмнопрстуфхцчшщъыьэюя"
M = len(ALPHABET)

CHAR_TO_IDX = {char: idx for idx, char in enumerate(ALPHABET)}
IDX_TO_CHAR = {idx: char for idx, char in enumerate(ALPHABET)}
ciphertext = [ch for ch in text.lower() if ch in CHAR_TO_IDX]
n=len(ciphertext)
r=14

MOST_FREQUENT_LANG_CHAR = "о"
x_star = CHAR_TO_IDX[MOST_FREQUENT_LANG_CHAR]

blocks = [ciphertext[i::r] for i in range(r)]

print(f"{'Блок i':<8} | {'Довжина':<8} | {'y* (найчастіша)':<16} | {'Кількість':<10} | {'k_i (індекс)':<12} | {'Символ ключа'}")
print("-" * 78)

key_indices = []

for i, b in enumerate(blocks):
    counts = Counter(b)
    y_star_char, count = counts.most_common(1)[0]
    y_star = CHAR_TO_IDX[y_star_char]

    k_i = (y_star - x_star) % M
    key_indices.append(k_i)
    
    print(f"{i:<8} | {len(b):<8} | {y_star_char} (індекс {y_star:<2})    | {count:<10} | {k_i:<12} | {IDX_TO_CHAR[k_i]}")

key_string = "".join(IDX_TO_CHAR[k] for k in key_indices)

print("\n" + "-" * 60)
print(f"Відновлений ключ: {key_string}")

decrypted_chars = []
for i, char in enumerate(ciphertext):
    y_i = CHAR_TO_IDX[char]
    k_i = key_indices[i % r]
    x_i = (y_i - k_i) % M
    decrypted_chars.append(IDX_TO_CHAR[x_i])

decrypted_text = "".join(decrypted_chars)

print("Розшифрування перших 500 символів:")
print("-" * 60)
print(decrypted_text[:500])

#иыутяьвиделмоятцикшйрвисящцйнйдолмойнитиьпувеннчйсвольаыхчравсзохроныомлелиаииописйвафколобанияяхнафноилсякийозу
#тслбышодчараъиморнотпульсадииатопориодкощебйнийчпределуноыношониемкводрйтномокорнятлицыниыикчислбркчторчеирраццо
#нйльнчедляпотлуцныхьмовпретлияомбчжествеынотрацсонеукояниыельцосопрясаеыокрьжностиядийметщамилюбйхсьщесывующихшр
#умовкйкивремнпещемевенияшаюаоыоднчгополюяакшротсвополофнохупродс