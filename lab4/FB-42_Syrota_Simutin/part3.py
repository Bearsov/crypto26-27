from math import gcd
from pathlib import Path

from part2 import generate_two_pairs


def extended_gcd(a, b):
    old_r, r = a, b
    old_x, x = 1, 0

    while r != 0:
        quotient = old_r // r
        old_r, r = r, old_r - quotient * r
        old_x, x = x, old_x - quotient * x

    return old_r, old_x


def modular_inverse(a, modulus):
    divisor, x = extended_gcd(a, modulus)

    if divisor != 1:
        raise ValueError("Обернений елемент не існує")

    return x % modulus


def GenerateKeyPair(p, q):
    if p == q:
        raise ValueError("p і q повинні бути різними")

    n = p * q
    phi = (p - 1) * (q - 1)
    e = 65537

    if not 1 < e < phi or gcd(e, phi) != 1:
        raise ValueError("Для цих p і q показник e = 65537 не підходить")

    d = modular_inverse(e, phi)

    public_key = (n, e)
    private_key = (d, p, q)

    return public_key, private_key


def save_keys(filename, public_a, private_a, public_b, private_b):
    n, e = public_a
    d, p, q = private_a

    n1, e1 = public_b
    d1, p1, q1 = private_b

    values = (
        ("p", p),
        ("q", q),
        ("n", n),
        ("e", e),
        ("d", d),
        ("p1", p1),
        ("q1", q1),
        ("n1", n1),
        ("e1", e1),
        ("d1", d1),
    )

    with open(filename, "w", encoding="utf-8") as file:
        for name, value in values:
            file.write(f"{name} = {value}\n")


if __name__ == "__main__":
    while True:
        p, q, p1, q1 = generate_two_pairs(256)

        try:
            public_a, private_a = GenerateKeyPair(p, q)
            public_b, private_b = GenerateKeyPair(p1, q1)
            break
        except ValueError:
            continue

    n, e = public_a
    d = private_a[0]

    n1, e1 = public_b
    d1 = private_b[0]

    phi = (p - 1) * (q - 1)

    print("Основні параметри абонента A:")
    print("p =", p)
    print("q =", q)
    print("n =", n)
    print("phi(n) =", phi)
    print("e =", e)
    print("d =", d)

    print("\nВідкритий ключ A (n, e):")
    print(public_a)
    print("Секретний ключ A (d, p, q):")
    print(private_a)

    print("\nВідкритий ключ B (n1, e1):")
    print(public_b)
    print("Секретний ключ B (d1, p1, q1):")
    print(private_b)

    print("\nПеревірка співвідношень для A:")
    print("p != q:", p != q)
    print("n = p * q:", n == p * q)
    print("2 <= e <= phi(n) - 1:", 2 <= e <= phi - 1)
    print("gcd(e, phi(n)) = 1:", gcd(e, phi) == 1)
    print("e * d mod phi(n) = 1:", e * d % phi == 1)

    print("\nПеревірка порядку модулів:")
    print("n <= n1:", n <= n1)

    filename = Path(__file__).resolve().with_name("keys.txt")
    save_keys(filename, public_a, private_a, public_b, private_b)

    print("\nКлючі збережено в:", filename)