from itertools import permutations
from math import gcd
from pathlib import Path
from common import ALPHABETS, M2, LANG_BIGRAMS, read, clean, inverse, solve_congruence, bigram_to_num, decrypt, encrypt, score
from lab1_common import bigram_freqs, top_n

BASE = Path(__file__).resolve().parent

def attack(text, alpha):
    top = [bg for bg, _ in top_n(bigram_freqs(text))]
    keys = {}
    no_roots = multiple = all_roots = rejected = 0
    for x1, x2 in permutations(LANG_BIGRAMS, 2):
        X1, X2 = bigram_to_num(x1, alpha), bigram_to_num(x2, alpha)
        for y1, y2 in permutations(top, 2):
            Y1, Y2 = bigram_to_num(y1, alpha), bigram_to_num(y2, alpha)
            roots = solve_congruence(X1 - X2, Y1 - Y2, M2)
            no_roots += not roots
            multiple += len(roots) > 1
            all_roots += len(roots)
            for a in roots:
                if gcd(a, M2) != 1:
                    rejected += 1
                    continue
                b = (Y1 - a * X1) % M2
                keys.setdefault((a, b), (x1, y1, x2, y2))

    found = []
    for (a, b), pairs in keys.items():
        pt = decrypt(text, a, b, alpha)
        f, r, bad = score(pt)
        if f > 0.20 and r < 0.05:
            found.append((bad, f, r, a, b, pairs, pt))
    found.sort(key=lambda item: (item[0], -item[1], item[2]))
    return top, (no_roots, multiple, all_roots, rejected, len(keys)), found


for name in ('06.txt', 'V6.txt'):
    text = clean(read(BASE / name))
    if len(text) % 2:
        raise ValueError(f'Непарна кількість літер у {name}')
    print(f'\nФайл {name}; літер: {len(text)}')
    accepted = []
    for label, alpha in zip('AB', ALPHABETS):
        top, stats, found = attack(text, alpha)
        print(f'Алфавіт {label}: {alpha}')
        print(f'Топ-5: {top}')
        print(f'400 зіставлень; без розв’язків: {stats[0]}; із кількома: {stats[1]}')
        print(f'Коренів a: {stats[2]}; відкинуто: {stats[3]}; різних ключів: {stats[4]}')
        print(f'Пройшли розпізнавач: {len(found)}')
        for bad, f, r, a, b, pairs, pt in found:
            print(f'a={a}, b={b}, a⁻¹={inverse(a, M2)}; о+а+е={f:.4f}; ф+щ+ь={r:.4f}; нетипових={bad}')
            print(f'Зіставлення: {pairs[0]}→{pairs[1]}, {pairs[2]}→{pairs[3]}')
            print(f'Початок: {pt[:130]}')
            accepted.append((bad, -f, r, label, a, b, pt))
    if accepted:
        bad, neg_f, r, label, a, b, pt = min(accepted)
        encrypted = encrypt(pt, a, b, ALPHABETS['AB'.index(label)])
        assert encrypted == text
        output = BASE / f'decrypted_{Path(name).stem}.txt'
        output.write_text(pt, encoding='utf-8')
        print(f'Найкращий кандидат: алфавіт {label}, a={a}, b={b}; файл: {output.name}')
    else:
        print('Кандидатів не знайдено')
