import random

from rsa_lab5 import (Encrypt, Decrypt, Sign, Verify, SendKey, ReceiveKey,
                      load_keys, to_hex, from_hex)

public_A, private_A, public_B, private_B = load_keys()
OUT_FILE = "server_values.txt"


def ask_hex(prompt):
    while True:
        try:
            return from_hex(input(prompt))
        except ValueError as err:
            print("  Помилка:", err)
            print("  Скопіюйте значення ще раз.")

def ask_server_key():
    n = ask_hex("  Modulus сервера (вкладка Server Key), hex: ")
    e = ask_hex("  Public exponent сервера, hex: ")
    return n, e

def random_message(bits=128):
    return random.getrandbits(bits) | (1 << (bits - 1))

def save(title, items):
    lines = [title]
    for name, value in items:
        lines.append(f"{name}:")
        lines.append(value)
        lines.append("")
    text = "\n".join(lines)
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        f.write(text)
    print("\n" + text)
    print(f"(значення також записано у файл {OUT_FILE})")


def check1():
    print("\n[1] Encrypt (наша реалізація) -> Decrypt на сервері")
    print("  Спершу на вкладці Server Key натисніть Get key (розмір 1024).")
    server_public = ask_server_key()
    M = random_message()
    C = Encrypt(M, server_public)
    save("Вкладка Decryption (режим Bytes): вставте Ciphertext",
         [("Message M (для порівняння)", to_hex(M)), ("Ciphertext C", to_hex(C))])
    print("Натисніть Decrypt: сервер має повернути Message = M.")

def check2():
    print("\n[2] Encrypt на сервері -> Decrypt (наша реалізація)")
    n, e = public_A
    M = random_message()
    save("Вкладка Encryption (режим Bytes): введіть Modulus, Public exponent, Message",
         [("Modulus (n абонента A)", to_hex(n)), ("Public exponent (e)", to_hex(e)),
          ("Message M", to_hex(M))])
    print("Натисніть Encrypt, скопіюйте Ciphertext із сайту.")
    C = ask_hex("  Ciphertext із сайту, hex: ")
    result = Decrypt(C, private_A)
    print("\nРозшифровано:", to_hex(result))
    print("Збігається з M:", result == M)

def check3():
    print("\n[3] Sign на сервері -> Verify (наша реалізація)")
    print("  Спершу Get key на вкладці Server Key (1024 біти).")
    server_public = ask_server_key()
    M = random_message()
    save("Вкладка Sign (режим Bytes): введіть Message", [("Message M", to_hex(M))])
    print("Натисніть Sign, скопіюйте Signature із сайту.")
    S = ask_hex("  Signature із сайту, hex: ")
    print("\nVerify(M, S):", Verify(M, S, server_public))
    print("Verify(M + 1, S) (змінене повідомлення):", Verify(M + 1, S, server_public))

def check4():
    print("\n[4] Sign (наша реалізація) -> Verify на сервері")
    n, e = public_A
    M = random_message()
    S = Sign(M, private_A)
    save("Вкладка Verification (режим Bytes): введіть усі чотири поля",
         [("Message M", to_hex(M)), ("Signature S", to_hex(S)),
          ("Modulus (n абонента A)", to_hex(n)), ("Public exponent (e)", to_hex(e))])
    print("Натисніть Verify: сервер має показати true.")

def check5():
    print("\n[5] SendKey (наша реалізація, абонент A) -> ReceiveKey на сервері")
    print("  Спершу Get key на вкладці Server Key (1024 біти: модуль сервера має бути більший за наш n).")
    server_public = ask_server_key()
    n, e = public_A
    k = random.randrange(1, n)
    try:
        k1, S1 = SendKey(k, private_A, server_public)
    except ValueError as err:
        print("\nПомилка:", err)
        print("Згенеруйте на сервері ключ більшого розміру (1024 біти).")
        return
    save("Вкладка Receive Key: введіть усі чотири поля",
         [("Key (k1)", to_hex(k1)), ("Signature (S1)", to_hex(S1)),
          ("Modulus (n абонента A)", to_hex(n)), ("Public exponent (e)", to_hex(e)),
          ("Наш ключ k (для порівняння)", to_hex(k))])
    print("Натисніть Receive: сервер має показати Key = k (можливо, з ведучим нулем) і Verification: true.")

def check6():
    print("\n[6] SendKey на сервері -> ReceiveKey (наша реалізація, абонент B)")
    print("  Спершу Get key на вкладці Server Key з розміром 256 біт (модуль сервера має бути меншим за n1).")
    server_public = ask_server_key()
    n1, e1 = public_B
    if server_public[0] > n1:
        print("\nМодуль сервера більший за n1: протокол не спрацює. Згенеруйте менший ключ (256 біт).")
        return
    save("Вкладка Send Key: введіть Modulus та Public exponent",
         [("Modulus (n1 абонента B)", to_hex(n1)), ("Public exponent (e1)", to_hex(e1))])
    print("Натисніть Send, скопіюйте Key та Signature із сайту.")
    k1 = ask_hex("  Key із сайту, hex: ")
    S1 = ask_hex("  Signature із сайту, hex: ")
    k = ReceiveKey(k1, S1, private_B, server_public)
    if k is None:
        print("\nПідпис не пройшов перевірку, ключ відхилено.")
        print("Перевірте, що Key і Signature взято з одного натискання Send.")
    else:
        print("\nКлюч прийнято, підпис вірний. k =", to_hex(k))
        bad = ReceiveKey(k1, (S1 + 1) % n1, private_B, server_public)
        print("Для зміненого на одиницю Signature результат:", bad)


CHECKS = {"1": check1, "2": check2, "3": check3, "4": check4, "5": check5, "6": check6}

while True:
    print("\n--- Перевірка із тестовим середовищем ---")
    print("1 - Encrypt (наша) -> Decrypt на сервері")
    print("2 - Encrypt на сервері -> Decrypt (наша)")
    print("3 - Sign на сервері -> Verify (наша)")
    print("4 - Sign (наша) -> Verify на сервері")
    print("5 - SendKey (наша) -> ReceiveKey на сервері")
    print("6 - SendKey на сервері -> ReceiveKey (наша)")
    print("0 - вихід")
    choice = input("Оберіть пункт: ").strip()
    if choice == "0":
        break
    if choice in CHECKS:
        CHECKS[choice]()
    else:
        print("Введіть число від 0 до 6")
