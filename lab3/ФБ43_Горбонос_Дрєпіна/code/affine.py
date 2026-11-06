from collections import Counter
from pathlib import Path
import csv
import json

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
RESULTS = ROOT / "results"
ARTIFACTS = ROOT / "artifacts"
CIPHER_FILE = DATA / "variant2_cipher.txt"
KP1_TEXT = DATA / "kp1" / "text_no_spaces.txt"

M = 31
N = M * M
ALPHABETS = {
    "ы27": "абвгдежзийклмнопрстуфхцчшщьыэюя",
    "ь27": "абвгдежзийклмнопрстуфхцчшщыьэюя",
}
LANG_TOP = ["ст", "но", "то", "на", "ен"]
FREQUENT = "оае"
RARE = "фщь"
T_FREQUENT = 0.24
T_RARE = 0.04
T_FORBIDDEN = 0.001


def egcd(a, b):
    r0, r1 = a, b
    u0, u1 = 1, 0
    v0, v1 = 0, 1
    while r1:
        q = r0 // r1
        r0, r1 = r1, r0 - q * r1
        u0, u1 = u1, u0 - q * u1
        v0, v1 = v1, v0 - q * v1
    return r0, u0, v0


def inverse(a, n):
    d, u, _ = egcd(a % n, n)
    if d != 1:
        raise ValueError(f"{a} не обертається за модулем {n}")
    return u % n


def solve_congruence(a, b, n):
    a, b = a % n, b % n
    d = egcd(a, n)[0]
    if b % d:
        return []
    a1, b1, n1 = a // d, b // d, n // d
    x0 = b1 * inverse(a1, n1) % n1 if n1 > 1 else 0
    return [x0 + i * n1 for i in range(d)]


def read_text(path):
    return "".join(Path(path).read_text(encoding="utf-8-sig").split())


def ngrams(text, n, step):
    return Counter(text[i:i + n] for i in range(0, len(text) - n + 1, step))


def bigram_to_int(bigram, alphabet):
    return alphabet.index(bigram[0]) * M + alphabet.index(bigram[1])


def int_to_bigram(x, alphabet):
    return alphabet[x // M] + alphabet[x % M]


def text_to_ints(text, alphabet):
    return [bigram_to_int(text[i:i + 2], alphabet) for i in range(0, len(text) - 1, 2)]


def decrypt(text, a, b, alphabet):
    a_inv = inverse(a, N)
    return "".join(int_to_bigram(a_inv * (y - b) % N, alphabet) for y in text_to_ints(text, alphabet))


def encrypt(text, a, b, alphabet):
    return "".join(int_to_bigram((a * x + b) % N, alphabet) for x in text_to_ints(text, alphabet))


def is_valid_key(a):
    return 0 < a < N and egcd(a, M)[0] == 1


def find_candidates(cipher_top, alphabet, lang_top=LANG_TOP):
    systems, keys = [], set()
    for i, x1 in enumerate(lang_top):
        for x2 in lang_top[i + 1:]:
            for y1 in cipher_top:
                for y2 in cipher_top:
                    if y1 == y2:
                        continue
                    X1, X2 = bigram_to_int(x1, alphabet), bigram_to_int(x2, alphabet)
                    Y1, Y2 = bigram_to_int(y1, alphabet), bigram_to_int(y2, alphabet)
                    roots = solve_congruence(X1 - X2, Y1 - Y2, N)
                    valid = [(a, (Y1 - a * X1) % N) for a in roots if is_valid_key(a)]
                    keys.update(valid)
                    systems.append({
                        "x1": x1, "x2": x2, "y1": y1, "y2": y2,
                        "d": egcd((X1 - X2) % N, N)[0],
                        "roots": len(roots), "valid": len(valid),
                    })
    return systems, sorted(keys)


def letter_share(text, letters):
    return sum(text.count(c) for c in letters) / len(text)


def cross_bigrams(text):
    return [text[i:i + 2] for i in range(1, len(text) - 1, 2)]


def forbidden_share(text, forbidden):
    pairs = cross_bigrams(text)
    return sum(p in forbidden for p in pairs) / len(pairs)


def load_forbidden():
    corpus = read_text(KP1_TEXT)
    seen = ngrams(corpus[:len(corpus) // 2], 2, 1)
    letters = sorted(set(corpus))
    return {x + y for x in letters for y in letters} - set(seen)


def measure(text, forbidden):
    return (
        letter_share(text, FREQUENT),
        letter_share(text, RARE),
        forbidden_share(text, forbidden),
    )


def is_russian(text, forbidden):
    c1, c2, c3 = measure(text, forbidden)
    return c1 >= T_FREQUENT and c2 <= T_RARE and c3 <= T_FORBIDDEN


def save_json(name, data):
    RESULTS.mkdir(exist_ok=True)
    (RESULTS / name).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def load_json(name):
    return json.loads((RESULTS / name).read_text(encoding="utf-8"))


def save_csv(name, header, rows):
    RESULTS.mkdir(exist_ok=True)
    with open(RESULTS / name, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)
