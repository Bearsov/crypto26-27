import random

SMALL_PRIMES = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47)


def mod_pow(base, exponent, modulus):
    result = 1

    while exponent > 0:
        if exponent % 2 == 1:
            result = result * base % modulus

        base = base * base % modulus
        exponent //= 2

    return result


def miller_rabin(n, rounds=40):
    if rounds < 1:
        raise ValueError("Кількість раундів має бути додатною")

    if n < 2:
        return False, None

    for prime in SMALL_PRIMES:
        if n == prime:
            return True, None
        if n % prime == 0:
            return False, None

    d = n - 1
    s = 0

    while d % 2 == 0:
        d //= 2
        s += 1

    example = None

    for i in range(rounds):
        a = random.randrange(2, n - 1)
        x = mod_pow(a, d, n)

        values = [x] if i == 0 else None
        passed = x == 1 or x == n - 1

        if not passed:
            for r in range(1, s):
                x = x * x % n

                if i == 0:
                    values.append(x)

                if x == n - 1:
                    passed = True
                    break

                if x == 1:
                    break

        if not passed:
            return False, None

        if i == 0:
            example = (s, d, a, values)

    return True, example


def generate_prime(bits=256):
    if bits < 8:
        raise ValueError("У цій реалізації довжина має бути від 8 біт")

    while True:
        candidate = random.getrandbits(bits)
        candidate |= (1 << (bits - 1)) | 1

        is_prime, example = miller_rabin(candidate)

        if is_prime:
            return candidate, example


if __name__ == "__main__":
    p, example = generate_prime(256)
    s, d, a, values = example

    print("Згенероване ймовірно просте число:")
    print("p =", p)
    print("Бітова довжина:", p.bit_length())

    print("\nПроміжні результати Міллера—Рабіна:")
    print(f"p - 1 = 2^{s} * {d}")
    print("s =", s)
    print("d =", d)
    print("Використана основа a =", a)
    print("x0 = a^d mod p =", values[0])

    for r, value in enumerate(values[1:], start=1):
        print(f"x{r} = x{r - 1}^2 mod p = {value}")

    if values[0] == 1:
        print("Раунд пройдено: x0 = 1")
    elif values[0] == p - 1:
        print("Раунд пройдено: x0 = p - 1")
    else:
        print("Раунд пройдено: один із наступних квадратів дорівнює p - 1")
