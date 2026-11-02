from pathlib import Path

ALPHABET = "абвгдежзийклмнопрстуфхцчшщьыэюя"
MODULUS = len(ALPHABET) ** 2
FOLDER = Path(__file__).resolve().parent


def normalize(text):
    text = text.lower().replace("ё", "е").replace("ъ", "ь")
    return "".join(char for char in text if char in ALPHABET)


def read_ciphertext():
    text = "".join((FOLDER / "05.txt").read_text(encoding="utf-8-sig").split())
    if not text or len(text) % 2 or any(char not in ALPHABET for char in text):
        raise ValueError("Шифртекст має містити парну кількість літер заданого алфавіту")
    return text


def extended_gcd(a, b):
    old_r, r = a, b
    old_u, u = 1, 0
    old_v, v = 0, 1
    while r != 0:
        q = old_r // r
        old_r, r = r, old_r - q * r
        old_u, u = u, old_u - q * u
        old_v, v = v, old_v - q * v
    if old_r < 0:
        return -old_r, -old_u, -old_v
    return old_r, old_u, old_v


def inverse(a, modulus):
    if modulus <= 1:
        raise ValueError("Модуль має бути більшим за 1")
    d, u, v = extended_gcd(a, modulus)
    if d != 1:
        raise ValueError("Оберненого елемента не існує")
    return u % modulus


def solve_congruence(a, b, modulus):
    if modulus < 1:
        raise ValueError("Модуль має бути додатним")
    d, u, v = extended_gcd(a, modulus)
    if b % d != 0:
        return []
    reduced_modulus = modulus // d
    first = (u * (b // d)) % reduced_modulus
    return [first + k * reduced_modulus for k in range(d)]


def bigram_number(bigram):
    return ALPHABET.index(bigram[0]) * 31 + ALPHABET.index(bigram[1])


def number_bigram(number):
    return ALPHABET[number // 31] + ALPHABET[number % 31]


def encrypt(text, a, b):
    inverse(a, MODULUS)
    if len(text) % 2:
        raise ValueError("Кількість літер має бути парною")
    result = []
    for i in range(0, len(text), 2):
        x = bigram_number(text[i:i + 2])
        result.append(number_bigram((a * x + b) % MODULUS))
    return "".join(result)


def decrypt(text, a, b):
    a_inverse = inverse(a, MODULUS)
    if len(text) % 2:
        raise ValueError("Кількість літер має бути парною")
    result = []
    for i in range(0, len(text), 2):
        y = bigram_number(text[i:i + 2])
        result.append(number_bigram(a_inverse * (y - b) % MODULUS))
    return "".join(result)


if __name__ == "__main__":
    print("Алфавіт:", ALPHABET)
    print("m =", len(ALPHABET), "m² =", MODULUS)
    print("Обернений до 72 за модулем 961:", inverse(72, 961))
    print("72x = 1 (mod 961):", solve_congruence(72, 1, 961))
    solutions = solve_congruence(31, 62, 961)
    print("31x = 62 (mod 961):", len(solutions), "розв'язок")
    print(", ".join(str(x) for x in solutions))
    print("31x = 1 (mod 961):", solve_congruence(31, 1, 961))
