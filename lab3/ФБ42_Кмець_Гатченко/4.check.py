from math import gcd
from affine import (ALPHABET, FOLDER, MODULUS, bigram_number, decrypt,
                    encrypt, extended_gcd, inverse, number_bigram,
                    read_ciphertext, solve_congruence)


if __name__ == "__main__":
    checked = 0
    for modulus in range(1, 21):
        for a in range(-modulus, modulus + 1):
            for b in range(modulus):
                expected = [x for x in range(modulus) if (a * x - b) % modulus == 0]
                actual = solve_congruence(a, b, modulus)
                if actual != expected:
                    raise ValueError("Помилка розв'язування лінійного порівняння")
                d, u, v = extended_gcd(a, modulus)
                if d != gcd(a, modulus) or a * u + modulus * v != d:
                    raise ValueError("Помилка розширеного алгоритму Евкліда")
                checked += 1
    print("Перевірено лінійних порівнянь:", checked)

    for a in range(MODULUS):
        try:
            value = inverse(a, MODULUS)
        except ValueError:
            if gcd(a, MODULUS) == 1:
                raise ValueError("Оборотний елемент помилково відкинуто")
        else:
            if gcd(a, MODULUS) != 1 or a * value % MODULUS != 1:
                raise ValueError("Помилка обернення")
    print("Обернені елементи перевірено для всіх 961 лишків")
    for x in range(MODULUS):
        if bigram_number(number_bigram(x)) != x:
            raise ValueError("Помилка нумерації біграм")
    print("Нумерацію всіх 961 біграми перевірено")

    ciphertext = read_ciphertext()
    a, b = map(int, (FOLDER / "key.txt").read_text(encoding="utf-8").split())
    plaintext = (FOLDER / "decrypted.txt").read_text(encoding="utf-8").strip()
    same = encrypt(plaintext, a, b) == ciphertext
    if not same or decrypt(ciphertext, a, b) != plaintext:
        raise ValueError("Повторне шифрування або розшифрування не збігається")
    all_bigrams = "".join(number_bigram(x) for x in range(MODULUS))
    for test_a, test_b in [(1, 0), (a, b), (960, 960)]:
        if decrypt(encrypt(all_bigrams, test_a, test_b), test_a, test_b) != all_bigrams:
            raise ValueError("Помилка обробки всіх біграм")
    print("Усі 961 біграму перевірено на 3 ключах")
    print(f"Ключ: a = {a}, b = {b}; обернений до a: {inverse(a, MODULUS)}")
    print("Повторне шифрування збігається:", same)
    print("Довжини текстів:", len(ciphertext), len(plaintext))
    print("Усі перевірки пройдено")
