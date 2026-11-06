def power_mod(b, e, m):
    r = 1
    b %= m
    while e:
        if e & 1:
            r = r * b % m
        b = b * b % m
        e >>= 1
    return r

def to_hex(n):
    return hex(n)[2:].upper()

def from_hex(s):
    return int(s.strip(), 16)

def main():
    print("=" * 60)
    print("ПУЛЬТ ДЛЯ РОБОТИ З ТЕСТОВИМ СЕРВЕРОМ RSA")
    print("=" * 60)
    print("Оберіть операцію:")
    print("1. Зашифрувати повідомлення ДЛЯ сервера (Пункт А)")
    print("2. Розшифрувати шифротекст ВІД сервера (Пункт Б)")
    print("3. Вийти")
    print("=" * 60)

    choice = input("Ваш вибір (1/2/3): ").strip()

    if choice == "1":
        print("\n--- РЕЖИМ 1: Шифрування для сервера ---")
        mod_str = input("Вставте Modulus сервера: ")
        exp_str = input("Вставте Public exponent: ")
        msg_str = input(
            "Введіть ваше повідомлення в HEX (наприклад, 123456789ABCDEF): "
        )

        n = from_hex(mod_str)
        e = from_hex(exp_str)
        M = from_hex(msg_str)

        C = power_mod(M, e, n)

        print("\n" + "-" * 50)
        print("ГОТОВО! Скопіюйте цей Ciphertext і вставте на сайті:")
        print(to_hex(C))
        print("-" * 50)

    elif choice == "2":
        print("\n--- РЕЖИМ 2: Розшифрування повідомлення від сервера ---")
        c_str = input("Вставте Ciphertext: ")
        d_str = input("Вставте ваш секретний ключ d: ")
        n_str = input("Вставте ваш модуль n: ")

        C = from_hex(c_str)
        d = from_hex(d_str)
        n = from_hex(n_str)

        M = power_mod(C, d, n)

        print("\n" + "-" * 50)
        print("РОЗШИФРОВАНО! Відкритий текст (HEX):")
        print(to_hex(M))
        print("-" * 50)


if __name__ == "__main__":
    main()