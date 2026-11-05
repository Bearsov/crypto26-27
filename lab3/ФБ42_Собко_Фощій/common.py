from collections import Counter
from math import gcd
from pathlib import Path

ALPHABETS = (
    'абвгдежзийклмнопрстуфхцчшщьыэюя',
    'абвгдежзийклмнопрстуфхцчшщыьэюя'
)
M = 31
M2 = M * M
LANG_BIGRAMS = ('ст', 'но', 'то', 'на', 'ен')
def read(path):
    data = Path(path).read_bytes()
    try:
        return data.decode('utf-8-sig')
    except UnicodeDecodeError:
        return data.decode('cp1251')
def clean(text, alpha=ALPHABETS[0]):
    text = text.lower().replace('ё', 'е').replace('ъ', 'ь')
    return ''.join(c for c in text if c in alpha)
def egcd(a, b):
    if b == 0:
        return abs(a), 1 if a >= 0 else -1, 0
    d, x, y = egcd(b, a % b)
    return d, y, x - (a // b) * y
def inverse(a, n):
    d, x, _ = egcd(a, n)
    return x % n if d == 1 else None
def solve_congruence(a, b, n):
    d = gcd(a, n)
    if b % d:
        return []
    k = n // d
    x = (inverse(a // d, k) * (b // d)) % k if k > 1 else 0
    return [x + i * k for i in range(d)]
def bigram_to_num(bg, alpha):
    return alpha.index(bg[0]) * M + alpha.index(bg[1])
def num_to_bigram(x, alpha):
    return alpha[x // M] + alpha[x % M]
def decrypt(text, a, b, alpha):
    inv = inverse(a, M2)
    if inv is None or len(text) % 2:
        raise ValueError('Некоректний ключ або довжина шифртексту')
    return ''.join(num_to_bigram((inv * (bigram_to_num(text[i:i+2], alpha) - b)) % M2, alpha)
                   for i in range(0, len(text), 2))
def encrypt(text, a, b, alpha):
    if len(text) % 2:
        raise ValueError('Непарна довжина тексту')
    return ''.join(num_to_bigram((a * bigram_to_num(text[i:i+2], alpha) + b) % M2, alpha)
                   for i in range(0, len(text), 2))
def score(text):
    counts = Counter(text)
    f = sum(counts[c] for c in 'оае') / len(text)
    r = sum(counts[c] for c in 'фщь') / len(text)
    bad = sum(text.count(bg) for bg in ('шы', 'щы', 'жы', 'чы', 'ьы', 'ыь', 'ьь', 'ыы', 'уь'))
    return f, r, bad
