import os
import math
import re
import random
from collections import Counter

ALPHABET = "абвгдежзийклмнопрстуфхцчшщъыьэюя"

def entropy(counter, n):
    total = sum(counter.values())
    return -sum((c / total) * math.log2(c / total) for c in counter.values()) / n

def get_ngrams(text, n, step):
    return Counter(text[i:i+n] for i in range(0, len(text) - n + 1, step))

def analyze_dataset(text, title, m):
    h0 = math.log2(m)
    
    chars = get_ngrams(text, 1, 1)
    h1_val = entropy(chars, 1)
    r1 = 1 - (h1_val / h0)
    
    bi_cross = get_ngrams(text, 2, 1)
    h2_cross = entropy(bi_cross, 2)
    r2_cross = 1 - (h2_cross / h0)
    
    bi_nocross = get_ngrams(text, 2, 2)
    h2_nocross = entropy(bi_nocross, 2)
    r2_nocross = 1 - (h2_nocross / h0)

    print(f"\n{title} (m = {m}, H0 = {h0:.4f}, довжина = {len(text)} симв.):")
    print(f"H1 = {h1_val:.4f}, R = {r1:.4f}")
    print("Топ-5 символів:", chars.most_common(5))
    
    print("\nПовна таблиця частот символів:")
    total_chars = sum(chars.values())
    for ch, cnt in sorted(chars.items(), key=lambda x: -x[1]):
        print(f"  '{ch}': {cnt} ({cnt/total_chars:.4f})")
        
    print(f"\nH2 (перетин) = {h2_cross:.4f}, R = {r2_cross:.4f}")
    print("Топ-5 біграм:", bi_cross.most_common(5))
    print(f"H2 (без перетину) = {h2_nocross:.4f}, R = {r2_nocross:.4f}")
    print("Топ-5 біграм:", bi_nocross.most_common(5))
    print(f"ΔH2 (різниця перетину) = {abs(h2_cross - h2_nocross):.6f}")

def main():
    random.seed(42)
    
    file_name = 'book.txt'
    if not os.path.exists(file_name):
        print("Файл book.txt не знайдено.")
        return

    size_mb = os.path.getsize(file_name) / (1024 * 1024)
    print(f"Обробка файлу: {file_name} ({size_mb:.2f} МБ)")

    with open(file_name, 'r', encoding='utf-8', errors='ignore') as f:
        raw = f.read().lower().replace('ё', 'е')

    text_with_spaces = re.sub(r'[^а-я]+', ' ', raw).strip()
    text_no_spaces = text_with_spaces.replace(' ', '')

    analyze_dataset(text_with_spaces, "1. Текст з пробілами", len(ALPHABET) + 1)
    analyze_dataset(text_no_spaces, "2. Текст без пробілів", len(ALPHABET))
    
    print("\n3. Дослідження розподілу символів:")
    print("Прогноз: H1(Б) < H1(А) < H1(В)")
    print("Послідовність Б детермінована, В має максимальну ентропію, А - посередині.")
    
    seq_a = text_with_spaces[:10000]
    seq_b = 'а' * 10000
    seq_v = ''.join(random.choices(ALPHABET + ' ', k=10000))

    print(f"Послідовність А (природний текст): H1 = {entropy(get_ngrams(seq_a, 1, 1), 1):.4f}")
    print(f"Послідовність Б (один символ):     H1 = {entropy(get_ngrams(seq_b, 1, 1), 1):.4f}")
    print(f"Послідовність В (рівноймовірна):   H1 = {entropy(get_ngrams(seq_v, 1, 1), 1):.4f}")

    print("\n4. Дослідження залежностей між символами:")
    print("Прогноз:")
    print("1. H1(Г) і H1(Д) будуть ідентичними.")
    print("2. H2(Д) буде суттєво меншим за H2(Г).")
    print("3. H2(без перетину) для Д впаде до нуля.")
    print("4. H2(перетин) для Д покаже ненульову ентропію.")
    
    seq_d = 'аб' * 5000
    g_chars = list(seq_d)
    random.shuffle(g_chars)
    seq_g = ''.join(g_chars)

    h1_g = entropy(get_ngrams(seq_g, 1, 1), 1)
    h2_g_cross = entropy(get_ngrams(seq_g, 2, 1), 2)
    h2_g_nocross = entropy(get_ngrams(seq_g, 2, 2), 2)

    h1_d = entropy(get_ngrams(seq_d, 1, 1), 1)
    h2_d_cross = entropy(get_ngrams(seq_d, 2, 1), 2)
    h2_d_nocross = entropy(get_ngrams(seq_d, 2, 2), 2)

    print(f"\nПослідовність Г (випадкова):")
    print(f"  H1 = {h1_g:.4f}, H2 (перетин) = {h2_g_cross:.4f}, H2 (без перетину) = {h2_g_nocross:.4f}")
    print(f"Послідовність Д (періодична 'аб'):")
    print(f"  H1 = {h1_d:.4f}, H2 (перетин) = {h2_d_cross:.4f}, H2 (без перетину) = {h2_d_nocross:.4f}")

if __name__ == '__main__':
    main()