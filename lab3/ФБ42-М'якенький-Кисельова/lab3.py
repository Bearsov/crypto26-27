import sys
from itertools import permutations

ALPHABET =  'абвгдежзийклмнопрстуфхцчшщьыэюя'
M = len(ALPHABET)
M2 = M * M

def gcd(a, b):
    while b:
        a, b = b, a % b
    return a

def inverse_by_modulo(a, m):
    a %= m
    r, r_next = a, m
    u, u_next = 1, 0
    while r_next:
        q = r // r_next
        r, r_next = r_next, r - q * r_next
        u, u_next = u_next, u - q * u_next
    if r != 1:
        return None
    return u % m

def solve_linear_comparison(a, b, n):
    b %= n
    d = gcd(a, n)
    if b % d != 0:
        return []
    a1, b1, n1 = a // d, b // d, n // d
    x0 = (b1 * inverse_by_modulo(a1, n1)) % n1 if n1 > 1 else 0
    return [(x0 + i * n1) % n for i in range(d)]

def bigram_to_num(bg):
    return ALPHABET.index(bg[0]) * M + ALPHABET.index(bg[1])

def num_to_bigram(num):
    return ALPHABET[num // M] + ALPHABET[num % M]

def top_bigrams(text, n=5):
    dist = {}
    for i in range(0, len(text) - 1, 2):
        bg = text[i:i + 2]
        dist[bg] = dist.get(bg, 0) + 1
    return sorted(dist, key=dist.get, reverse=True)[:n]

def decrypt(a, b, text):
    a_inv = inverse_by_modulo(a, M2)
    out = []
    for i in range(0, len(text) - 1, 2):
        y = bigram_to_num(text[i:i + 2])
        out.append(num_to_bigram((a_inv * (y - b)) % M2))
    return ''.join(out)

def find_keys(X1, X2, Y1, Y2):
    keys = []
    for a in solve_linear_comparison(X1 - X2, Y1 - Y2, M2):
        if gcd(a, M2) != 1:
            continue
        b = (Y1 - a * X1) % M2
        keys.append((a, b))
    return keys

FORBIDDEN = ['аь', 'оь', 'уь', 'ыь', 'эь', 'юь', 'яь', 'еь', 'иь', 'ьь', 'ьы', 'ьй',
             'жы', 'шы', 'щы', 'чы', 'гы', 'кы', 'хы', 'йь', 'ыы', 'ээ', 'юю', 'яя',
             'щц', 'цщ', 'жщ', 'щж', 'фщ', 'щф', 'ьа', 'ьэ', 'ьо']
COMMON = 'оаеинт'    
RARE = 'фщь'          

def is_meaningful(text):
    n = len(text)
    common = sum(text.count(c) for c in COMMON) / n   # у рос. мові ~0.45
    rare = sum(text.count(c) for c in RARE) / n       # ~0.02-0.03
    forb = sum(text.count(f) for f in FORBIDDEN) / (n - 1)
    return common > 0.38 and rare < 0.06 and forb < 0.01

def score(text):
    n = len(text)
    common = sum(text.count(c) for c in COMMON) / n
    forb = sum(text.count(f) for f in FORBIDDEN) / (n - 1)
    return common - 5 * forb

def read_text(path):
    raw = open(path, encoding='utf-8').read().lower()
    return ''.join(c for c in raw if c in ALPHABET)  

def attack(ciphertext, clear_top):
    cipher_top = top_bigrams(ciphertext, 5)
    print("Найчастіші біграми мови:     ", clear_top)
    print("Найчастіші біграми шифртексту:", cipher_top)

    clear = [bigram_to_num(b) for b in clear_top]
    cipher = [bigram_to_num(b) for b in cipher_top]

    found = []
    seen = set()
    for i, j in permutations(range(5), 2):
        for k, l in permutations(range(5), 2):
            for (a, b) in find_keys(clear[i], clear[j], cipher[k], cipher[l]):
                if (a, b) in seen:
                    continue
                seen.add((a, b))
                text = decrypt(a, b, ciphertext)
                if is_meaningful(text):
                    found.append((score(text), a, b, text,
                                  (clear_top[i], clear_top[j], cipher_top[k], cipher_top[l])))
    print(f"Перевірено кандидатів на ключ: {len(seen)}")
    found.sort(reverse=True)
    return found

def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "variant_10.txt"
    ciphertext = read_text(path)
    print(f"Файл: {path}, довжина шифртексту: {len(ciphertext)}")
    most_common_cleartext = ["ст", "но", "то", "на", "ен"]
    found = attack(ciphertext, most_common_cleartext)
    if not found:
        print("Змістовного тексту не знайдено")
        return
    for sc, a, b, text, pairs in found[:3]:
        print(f"\nКлюч: a={a}, b={b}  (X*={pairs[0]}, X**={pairs[1]} -> Y*={pairs[2]}, Y**={pairs[3]}), score={sc:.3f}")
        print(text[:300])
    best = found[0]
    open("decrypted_" + path, "w", encoding="utf-8").write(best[3])
    print(f"\nПовний розшифрований текст записано у decrypted_{path}")

if __name__ == "__main__":
    main()
