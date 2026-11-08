from collections import Counter
from itertools import permutations
import os

DIR = os.path.dirname(os.path.abspath(__file__))
ALPHABET = "абвгдежзийклмнопрстуфхцчшщыьэюя"
M = len(ALPHABET); M2 = M * M
IDX = {c: i for i, c in enumerate(ALPHABET)}

def egcd(a, b): # алгоритм евкліда
    u0, u1, v0, v1 = 1, 0, 0, 1
    while b:
        q = a // b
        a, b = b, a - q * b
        u0, u1 = u1, u0 - q * u1
        v0, v1 = v1, v0 - q * v1
    return a, u0, v0

def inv(a, n): # обернений елемень
    g, u, _ = egcd(a % n, n)
    return u % n if g == 1 else None

def solve_lin(a, b, n): # розв лінійного рівняння
    a, b = a % n, b % n
    d, _, _ = egcd(a, n)
    if b % d:
        return []
    a1, b1, n1 = a // d, b // d, n // d
    x0 = (b1 * inv(a1, n1)) % n1 if n1 > 1 else 0
    return [x0 + k * n1 for k in range(d)]

def bigram_to_num(s):  return IDX[s[0]] * M + IDX[s[1]]           # Біграми в числове значення та навпаки
def num_to_bigram(x):  return ALPHABET[x // M] + ALPHABET[x % M]  #

def top_bigrams(text, k=5): # найпопулярнішій біграми
    bg = [text[i:i+2] for i in range(0, len(text) - 1, 2)]
    return [b for b, _ in Counter(bg).most_common(k)]

def decrypt(text, a, b):
    ai = inv(a, M2)
    out = []
    for i in range(0, len(text) - 1, 2):
        out.append(num_to_bigram((ai * (bigram_to_num(text[i:i+2]) - b)) % M2))
    return "".join(out)

#FORBIDDEN = ["аь","еь","ыь","ьь","йь","оь","уь","яь","юь","жы","шы","щы","чы","щю","чя","щя","фь","ьы","ьй","йы","йй","ьь"]
COMMON_CHARS = "оеаинтслвр"
def is_meaningful(t):
#    if any(f in t for f in FORBIDDEN):
#        return False

    match_count = sum(1 for c in t if c in COMMON_CHARS)
    return (match_count / len(t)) > 0.60

RU_TOP_BG = ['то', 'ст', 'на', 'ов', 'ал', 'го', 'он', 'не', 'но', 'ко', 'ен', 'по', 'ос', 'ра', 'от']

def attack(cipher, RU_TOP_BG=RU_TOP_BG):
    cip_top = top_bigrams(cipher, 5)
    X = [bigram_to_num(x) for x in RU_TOP_BG]
    Y = [bigram_to_num(y) for y in cip_top]
    found, seen = [], set()
    for (x1, x2) in permutations(X, 2):
        for (y1, y2) in permutations(Y, 2):
            for a in solve_lin(x1 - x2, y1 - y2, M2):
                if egcd(a, M2)[0] != 1:
                    continue
                b = (y1 - a * x1) % M2
                if (a, b) in seen: continue
                seen.add((a, b))
                pt = decrypt(cipher, a, b)
                if is_meaningful(pt):
                    found.append((a, b, pt))
    return found


cipher = open(os.path.join(DIR, "03.txt"), encoding="utf-8").read().replace("\n", "").strip()
print("Топ-5 біграм шифртексту:", top_bigrams(cipher))
output_path = os.path.join(DIR, "decrypted.txt")
results = attack(cipher)
for a, b, pt in results:
    print(f"\nКЛЮЧ: a={a}, b={b}\n{pt[:300]}")
if len(results)==1:
    a, b, pt = results[0]
    with open(output_path, "w", encoding="utf-8") as f:
            f.write(pt)
