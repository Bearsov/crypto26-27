import collections
import itertools

ALPHABET = "абвгдежзийклмнопрстуфхцчшщыьэюя"
M = len(ALPHABET)
M2 = M * M
#1
def egcd(a, b):
    if a == 0:
        return (b, 0, 1)
    g, y, x = egcd(b % a, a)
    return (g, x - (b // a) * y, y)

def mod_inverse(a, m):
    g, x, _ = egcd(a % m, m)
    if g != 1:
        return None
    return x % m

def solve_linear_congruence(a, b, n):
    g, _, _ = egcd(a, n)
    if b % g != 0:
        return []
    a1, b1, n1 = a // g, b // g, n // g
    inv_a1 = mod_inverse(a1, n1)
    if inv_a1 is None:
        return []
    x0 = (b1 * inv_a1) % n1
    return [(x0 + i * n1) % n for i in range(g)]

def bg_to_int(bg):
    return ALPHABET.index(bg[0]) * M + ALPHABET.index(bg[1])

def int_to_bg(val):
    return ALPHABET[val // M] + ALPHABET[val % M]

def decrypt_text(ciphertext, a, b):
    inv_a = mod_inverse(a, M2)
    if inv_a is None:
        return ""
    out = []
    for i in range(0, len(ciphertext) - 1, 2):
        y = bg_to_int(ciphertext[i:i + 2])
        x = (inv_a * (y - b)) % M2
        out.append(int_to_bg(x))
    return "".join(out)
#2
def load_text(filename):
    raw = None
    for enc in ("utf-8", "cp1251"):
        try:
            with open(filename, "r", encoding=enc) as f:
                raw = f.read()
            break
        except UnicodeDecodeError:
            continue
    if raw is None:
        raise ValueError(f"Не вдалося прочитати файл {filename}")
    raw = raw.lower().replace("\u0451", "\u0435").replace("\u044a", "\u044c")
    return "".join(c for c in raw if c in ALPHABET)

TOP_PLAIN = ["ст", "но", "то", "на", "ен"]

def top_bigrams(text, n):
    bgs = [text[i:i + 2] for i in range(0, len(text) - 1, 2)]
    return [bg for bg, _ in collections.Counter(bgs).most_common(n)]
#3
def generate_candidates(top_plain, top_cipher):
    candidates = collections.defaultdict(list)
    pairs = list(itertools.product(top_plain, top_cipher))
    for (x1s, y1s), (x2s, y2s) in itertools.product(pairs, repeat=2):
        if x1s == x2s or y1s == y2s:
            continue
        x1, y1 = bg_to_int(x1s), bg_to_int(y1s)
        x2, y2 = bg_to_int(x2s), bg_to_int(y2s)
        dx = (x1 - x2) % M2
        dy = (y1 - y2) % M2
        for a in solve_linear_congruence(dx, dy, M2):
            if egcd(a, M2)[0] != 1:
                continue
            b = (y1 - a * x1) % M2
            candidates[(a, b)].append((x1s, y1s, x2s, y2s))
    return candidates
#5
RU_FREQ = {
    'о': 10.97, 'е': 8.45, 'а': 8.01, 'и': 7.35, 'н': 6.70, 'т': 6.26,
    'с': 5.47, 'р': 4.73, 'в': 4.54, 'л': 4.40, 'к': 3.49, 'м': 3.21,
    'д': 2.98, 'п': 2.81, 'у': 2.62, 'я': 2.01, 'ы': 1.90, 'ь': 1.74,
    'г': 1.70, 'з': 1.64, 'б': 1.59, 'ч': 1.45, 'й': 1.21, 'х': 0.97,
    'ж': 0.94, 'ш': 0.72, 'ю': 0.64, 'ц': 0.49, 'щ': 0.36, 'э': 0.33,
    'ф': 0.27,
}
COMMON_LETTERS = "оеаинтс"
RARE_LETTERS = "фщь"
FORBIDDEN_BIGRAMS = ['аь', 'оь', 'уь', 'еь', 'иь', 'ыь', 'эь', 'юь', 'яь', 'йь',
                     'ьь', 'чщ', 'щч', 'шщ', 'щш']

def is_readable_russian(text):
    if len(text) < 50:
        return False
    if any(f in text for f in FORBIDDEN_BIGRAMS):
        return False
    n = len(text)
    common_share = sum(text.count(c) for c in COMMON_LETTERS) / n
    rare_share = sum(text.count(c) for c in RARE_LETTERS) / n
    return common_share >= 0.40 and rare_share <= 0.05

def chi_square_score(text):
    n = len(text)
    chi = 0.0
    for ch, p in RU_FREQ.items():
        expected = p / 100 * n
        observed = text.count(ch)
        chi += (observed - expected) ** 2 / expected
    return chi

def check_criteria(text):
    if len(text) < 50:
        return "short"
    for f in FORBIDDEN_BIGRAMS:
        if f in text:
            return "forbidden:" + f
    n = len(text)
    common = sum(text.count(c) for c in COMMON_LETTERS) / n
    if common < 0.40:
        return "common=%.3f" % common
    rare = sum(text.count(c) for c in RARE_LETTERS) / n
    if rare > 0.05:
        return "rare=%.3f" % rare
    return "ok"

def attack_affine(filename, n_top=5):
    text = load_text(filename)
    print(f"Довжина очищеного шифртексту: {len(text)} символів")

    top_cipher = top_bigrams(text, n_top)
    print(f"Топ-{n_top} біграм шифртексту: {top_cipher}")
    print(f"Топ-{n_top} біграм мови: {TOP_PLAIN}\n")

    candidates = generate_candidates(TOP_PLAIN[:n_top], top_cipher)
    print(f"Знайдено кандидатів на ключ: {len(candidates)}\n")
#4
    rows = []
    for (a, b), pairs in candidates.items():
        plain = decrypt_text(text, a, b)
        reason = check_criteria(plain)
        rows.append((a, b, reason, chi_square_score(plain), pairs, plain))

    # Зведення за причинами відхилення
    stats = collections.Counter(r[2].split(":")[0].split("=")[0] for r in rows)
    print("Результати перевірки критеріїв:")
    for key in ("forbidden", "common", "rare", "short", "ok"):
        print(f"  {key:10s}: {stats.get(key, 0)}")
    print()

    # Медіана χ² для відхилених кандидатів (для контрольного питання 6)
    rejected_chi = sorted(r[3] for r in rows if r[2] != "ok")
    if rejected_chi:
        median = rejected_chi[len(rejected_chi) // 2]
        print(f"χ² відхилених кандидатів: мін={rejected_chi[0]:.1f}, "
              f"медіана={median:.1f}, макс={rejected_chi[-1]:.1f}\n")

    # Повна таблиця всіх кандидатів (для звіту)
    with open("candidates_V2.txt", "w", encoding="utf-8") as f:
        f.write("a\tb\tрезультат\tchi2\tпари\n")
        for a, b, reason, chi, pairs, _ in sorted(rows, key=lambda r: r[3]):
            f.write(f"{a}\t{b}\t{reason}\t{chi:.1f}\t{pairs[0]}\n")

    passed = sorted((r for r in rows if r[2] == "ok"), key=lambda r: r[3])
    with open("decrypted_V2.txt", "w", encoding="utf-8") as out:
        for a, b, _, chi, pairs, plain in passed:
            out.write(f"Ключ: a={a}, b={b}, chi2={chi:.1f}\n")
            out.write(f"Пари, що дали ключ: {pairs}\n")
            out.write(plain + "\n\n")

    if not passed:
        print("Осмислених текстів не знайдено.")
        return

    print(f"Пройшли перевірку: {len(passed)}\n")
    for a, b, _, chi, pairs, plain in passed[:5]:
        print(f"[*] a={a}, b={b}, chi2={chi:.1f}, пара: {pairs[0]}")
        print(f"    {plain[:120]}...\n")
    print("Файли: decrypted_V2.txt (осмислені), candidates_V2.txt (усі кандидати)")

if __name__ == "__main__":
    attack_affine("V2.txt")