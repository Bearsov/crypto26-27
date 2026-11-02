
from __future__ import annotations

import argparse
from collections import Counter
from itertools import permutations
from math import gcd, log2
from pathlib import Path

ALPHABET = 'абвгдежзийклмнопрстуфхцчшщьыэюя'
M = len(ALPHABET)
MOD = M * M
LANGUAGE_BIGRAMS = ('ст', 'но', 'то', 'на', 'ен')
COMMON_LETTERS = 'оае'
RARE_LETTERS = 'фщь'
COMMON_MIN = 0.20
RARE_MAX = 0.05


def normalize(text: str) -> str:
    text = text.lower().replace('ё', 'е').replace('ъ', 'ь')
    return ''.join(c for c in text if c in ALPHABET)


def extended_gcd(a: int, b: int) -> tuple[int, int, int]:
    """Returns (g,x,y) satisfying ax + by = g = gcd(a,b)."""
    old_r, r = a, b
    old_s, s = 1, 0
    old_t, t = 0, 1
    while r:
        q = old_r // r
        old_r, r = r, old_r - q * r
        old_s, s = s, old_s - q * s
        old_t, t = t, old_t - q * t
    return old_r, old_s, old_t


def inverse_mod(a: int, mod: int) -> int | None:
    g, x, _ = extended_gcd(a % mod, mod)
    return x % mod if g == 1 else None


def solve_congruence(a: int, b: int, mod: int) -> list[int]:
    """All residues x in [0,mod) satisfying a*x == b (mod mod)."""
    a %= mod
    b %= mod
    d = gcd(a, mod)
    if b % d != 0:
        return []
    reduced_mod = mod // d
    if reduced_mod == 1:
        return list(range(mod))
    inv = inverse_mod(a // d, reduced_mod)
    assert inv is not None
    first = (b // d * inv) % reduced_mod
    return [first + i * reduced_mod for i in range(d)]


def bigram_number(bg: str) -> int:
    return ALPHABET.index(bg[0]) * M + ALPHABET.index(bg[1])


def number_bigram(value: int) -> str:
    if not (0 <= value < MOD):
        raise ValueError('Bigram number must be between 0 and 960')
    return ALPHABET[value // M] + ALPHABET[value % M]


def bigram_stats(text: str) -> Counter[str]:
    """Non-overlapping bigrams (positions 0-1, 2-3, ...)."""
    return Counter(text[i:i+2] for i in range(0, len(text)-1, 2))


def encrypt(text: str, a: int, b: int) -> str:
    if gcd(a, MOD) != 1:
        raise ValueError('a must be coprime with 961')
    if len(text) % 2:
        raise ValueError('Input length must be even')
    return ''.join(number_bigram((a * bigram_number(text[i:i+2]) + b) % MOD)
                   for i in range(0, len(text), 2))


def decrypt(text: str, a: int, b: int) -> str:
    ainv = inverse_mod(a, MOD)
    if ainv is None:
        raise ValueError('Noninvertible key a')
    if len(text) % 2:
        raise ValueError('Input length must be even')
    return ''.join(number_bigram((ainv * (bigram_number(text[i:i+2]) - b)) % MOD)
                   for i in range(0, len(text), 2))


def candidates_from_pairs(x1: str, x2: str, y1: str, y2: str) -> list[tuple[int, int]]:
    X1, X2 = bigram_number(x1), bigram_number(x2)
    Y1, Y2 = bigram_number(y1), bigram_number(y2)
    result = []
    for a in solve_congruence(X1-X2, Y1-Y2, MOD):
        if gcd(a, MOD) == 1:
            b = (Y1-a*X1) % MOD
            result.append((a, b))
    return result


def shares(text: str) -> tuple[float, float]:
    counts = Counter(text)
    n = len(text)
    return (sum(counts[c] for c in COMMON_LETTERS) / n,
            sum(counts[c] for c in RARE_LETTERS) / n)


def entropy(text: str) -> float:
    counts = Counter(text)
    n = len(text)
    return -sum((c/n) * log2(c/n) for c in counts.values())


def format_table(stats: Counter[str], n: int = 5) -> list[str]:
    total = sum(stats.values())
    return [f'{bg:>8} | {bigram_number(bg):>3} | {cnt:>5} | {cnt/total:>9.5f}'
            for bg, cnt in stats.most_common(n)]


def run(cipher_file: Path, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    raw = cipher_file.read_text(encoding='utf-8-sig')
    ciphertext = normalize(raw)
    if len(ciphertext) < 2 or len(ciphertext) % 2:
        raise ValueError('The normalized ciphertext must have an even positive length')
    unknown = {c for c in raw.lower().replace('ё','е').replace('ъ','ь')
               if c.isalpha() and c not in ALPHABET}
    if unknown:
        raise ValueError(f'Unexpected alphabetic characters: {sorted(unknown)}')

    report: list[str] = []
    def write(s: str = '') -> None:
        print(s)
        report.append(s)

    write('ЛАБОРАТОРНА №3 — АФІННИЙ ШИФР БІГРАМ — ВАРІАНТ 9')
    write(f'Алфавіт: {ALPHABET}')
    write(f'm = {M}; m² = {MOD}; довжина = {len(ciphertext)} символів; '
          f'{len(ciphertext)//2} неперетинних біграм')
    write()
    write('1. ТОП-5 БІГРАМ ШИФРТЕКСТУ')
    write(' біграма |   Y | к-сть |    частка')
    cipher_stats = bigram_stats(ciphertext)
    for line in format_table(cipher_stats):
        write(line)
    write()
    write('2. ВІДОМІ ЧАСТІ БІГРАМИ ВІДКРИТОГО ТЕКСТУ')
    for bg in LANGUAGE_BIGRAMS:
        write(f'{bg} -> {bigram_number(bg)}')
    write()

    candidates: dict[tuple[int, int], tuple[str, str, str, str]] = {}
    systems = 0
    no_valid_key = 0
    with_multiple = 0
    cipher_top = [bg for bg, _ in cipher_stats.most_common(5)]
    for x1, x2 in permutations(LANGUAGE_BIGRAMS, 2):
        for y1, y2 in permutations(cipher_top, 2):
            systems += 1
            found = candidates_from_pairs(x1, x2, y1, y2)
            if not found:
                no_valid_key += 1
            if len(found) > 1:
                with_multiple += 1
            for key in found:
                candidates.setdefault(key, (x1,x2,y1,y2))
    write('3. ПЕРЕБІР КЛЮЧІВ')
    write(f'Розглянуто систем: {systems}')
    write(f'Без допустимих ключів: {no_valid_key}')
    write(f'Систем із кількома допустимими ключами: {with_multiple}')
    write(f'Унікальних кандидатів: {len(candidates)}')
    write()

    tested = []
    for (a,b), origin in candidates.items():
        pt = decrypt(ciphertext, a, b)
        common, rare = shares(pt)
        acceptable = common >= COMMON_MIN and rare <= RARE_MAX
        tested.append((acceptable, common, rare, a, b, origin, pt))
    tested.sort(key=lambda x: (-int(x[0]), -x[1], x[2]))
    accepted = [x for x in tested if x[0]]
    write('4. КРИТЕРІЙ РОЗПІЗНАВАННЯ ТЕКСТУ')
    write(f'Частка о,а,е >= {COMMON_MIN:.2f}; частка ф,щ,ь <= {RARE_MAX:.2f}')
    write(f'Кандидатів, які пройшли критерій: {len(accepted)}')
    write('Найкращі кандидати:')
    for item in tested[:10]:
        ok, common, rare, a, b, origin, pt = item
        write(f'a={a:>3}, b={b:>3}; оае={common:.4f}; фщь={rare:.4f}; '
              f'accepted={ok}; text={pt[:90]}')
    write()

    if not accepted:
        write('Автоматичний критерій не знайшов достовірного ключа: '
              'перевірте алфавіт та дані; нічого не вгадуємо.')
        (output_dir/'results.txt').write_text('\n'.join(report)+'\n', encoding='utf-8')
        return
    
    if len(accepted) > 1:
        write('УВАГА: кілька ключів пройшли критерій; перевірте зміст текстів вручну.')
    for index, (_,common,rare,a,b,origin,pt) in enumerate(accepted, start=1):
        name = 'decrypted_09.txt' if len(accepted) == 1 else f'decrypted_09_candidate_{index}.txt'
        (output_dir/name).write_text(pt+'\n', encoding='utf-8')
        assert encrypt(pt,a,b) == ciphertext, 'Round-trip verification failed'
        write(f'5. РЕЗУЛЬТАТ №{index}: a={a}, b={b}, inverse(a)={inverse_mod(a,MOD)}')
        write(f'Зіставлення: {origin[0]} -> {origin[2]}; {origin[1]} -> {origin[3]}')
        write(f'H1={entropy(pt):.5f} біт/символ; оае={common:.5f}; фщь={rare:.5f}')
        write(f'Початок: {pt[:260]}')
        write(f'Повторне шифрування підтверджено: True; файл: {name}')
    (output_dir/'results.txt').write_text('\n'.join(report)+'\n', encoding='utf-8')
    write('Протокол обчислень збережено у results.txt')


def self_test() -> None:
    assert M == 31
    assert extended_gcd(314, MOD)[0] == 1
    assert solve_congruence(31, 31, 961) == list(range(1,961,31))
    assert solve_congruence(31, 1, 961) == []
    text = 'мамапошламытьпосудуи'
    assert decrypt(encrypt(text,314,34),314,34) == text
    print('SELF TEST: OK')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('ciphertext', nargs='?', default='09.txt', type=Path,
                        help='Path to variant 9 UTF-8 ciphertext (default: 09.txt)')
    parser.add_argument('--out', type=Path, default=Path('.'),
                        help='Folder for decrypted_09.txt and results.txt')
    parser.add_argument('--test', action='store_true', help='Run mathematical self-tests')
    args = parser.parse_args()
    if args.test:
        self_test()
    else:
        run(args.ciphertext, args.out)
