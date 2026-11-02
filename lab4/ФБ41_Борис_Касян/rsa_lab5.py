import json
import os
import random
from math import gcd
from pathlib import Path

os.chdir(Path(__file__).resolve().parent)


def extended_euclid(a, b):
    old_r, r = a, b
    old_s, s = 1, 0
    while r != 0:
        q = old_r // r
        old_r, r = r, old_r - q * r
        old_s, s = s, old_s - q * s
    return old_r, old_s

def modular_inverse(a, m):
    g, x = extended_euclid(a, m)
    if g != 1:
        raise ValueError("Обернений елемент не існує")
    return x % m

def to_hex(x):
    return format(x, "X")

def from_hex(s):
    s = s.strip().replace(" ", "").replace("\n", "").replace("\r", "")
    if s.lower().startswith("0x"):
        s = s[2:]
    bad = [(i, c) for i, c in enumerate(s) if c not in "0123456789abcdefABCDEF"]
    if not s or bad:
        raise ValueError(f"Некоректне hex-значення. Недопустимі символи (позиція, символ): {bad[:5]}")
    return int(s, 16)

def load_keys(filename="rsa_keys.json"):
    with open(filename, "r", encoding="utf-8") as f:
        keys = json.load(f)
    public_A = (keys["A"]["public"]["n"], keys["A"]["public"]["e"])
    private_A = (keys["A"]["private"]["d"], keys["A"]["private"]["p"], keys["A"]["private"]["q"])
    public_B = (keys["B"]["public"]["n"], keys["B"]["public"]["e"])
    private_B = (keys["B"]["private"]["d"], keys["B"]["private"]["p"], keys["B"]["private"]["q"])
    return public_A, private_A, public_B, private_B


def GenerateKeyPair(p, q):
    if p == q:
        raise ValueError("Числа p і q повинні бути різними")
    n = p * q
    phi = (p - 1) * (q - 1)
    e = 65537
    if e >= phi or gcd(e, phi) != 1:
        while True:
            e = random.randrange(2, phi)
            if gcd(e, phi) == 1:
                break
    d = modular_inverse(e, phi)
    return (n, e), (d, p, q)

def Encrypt(message, public_key):
    n, e = public_key
    if not 0 <= message < n:
        raise ValueError("Повідомлення повинно бути в межах 0 <= M < n")
    return pow(message, e, n)

def Decrypt(ciphertext, private_key):
    d, p, q = private_key
    n = p * q
    if not 0 <= ciphertext < n:
        raise ValueError("Криптограма повинна бути в межах 0 <= C < n")
    return pow(ciphertext, d, n)

def Sign(message, private_key):
    d, p, q = private_key
    n = p * q
    if not 0 <= message < n:
        raise ValueError("Повідомлення повинно бути в межах 0 <= M < n")
    return pow(message, d, n)

def Verify(message, signature, public_key):
    n, e = public_key
    if not 0 <= message < n or not 0 <= signature < n:
        return False
    return pow(signature, e, n) == message

def SendKey(k, sender_private_key, receiver_public_key):

    d, p, q = sender_private_key
    n = p * q
    n1, _ = receiver_public_key
    if not 0 < k < n:
        raise ValueError("Ключ k повинен задовольняти 0 < k < n")
    if n > n1:
        raise ValueError("Потрібно n <= n1 (модуль відправника не більший за модуль отримувача)")
    S = Sign(k, sender_private_key)            # S  = k^d mod n
    k1 = Encrypt(k, receiver_public_key)       # k1 = k^e1 mod n1
    S1 = Encrypt(S, receiver_public_key)       # S1 = S^e1 mod n1
    return k1, S1

def ReceiveKey(k1, S1, receiver_private_key, sender_public_key):
    k = Decrypt(k1, receiver_private_key)      # k = k1^d1 mod n1
    S = Decrypt(S1, receiver_private_key)      # S = S1^d1 mod n1
    if not Verify(k, S, sender_public_key):    # k == S^e mod n 
        return None
    return k


#   Демонстрація одного виконання протоколу A -> B 

if __name__ == "__main__":
    public_A, private_A, public_B, private_B = load_keys()
    n, e = public_A
    n1, e1 = public_B

    print("\n-----ЗАВДАННЯ 5. ПРОТОКОЛ КОНФІДЕНЦІЙНОГО РОЗСИЛАННЯ КЛЮЧІВ-----")
    print("\nПеревірка n <= n1:", n <= n1)

    print("\n-----ВІДПРАВНИК (A)-----")
    k = random.randrange(1, n)
    print("1. Випадковий ключ 0 < k < n:")
    print("   k =", k)
    S = Sign(k, private_A)
    print("2. Підпис (секретний ключ A): S = k^d mod n")
    print("   S =", S)
    k1, S1 = SendKey(k, private_A, public_B)
    print("3. Шифрування (відкритий ключ B): k1 = k^e1 mod n1")
    print("   k1 =", k1)
    print("4. Шифрування підпису (відкритий ключ B): S1 = S^e1 mod n1")
    print("   S1 =", S1)
    print("\n5. По відкритому каналу від A до B передаються (k1, S1)")

    print("\n-----ОТРИМУВАЧ (B)-----")
    k_rec = ReceiveKey(k1, S1, private_B, public_A)
    print("6. Розшифрування (секретний ключ B):")
    print("   k = k1^d1 mod n1 =", Decrypt(k1, private_B))
    print("   S = S1^d1 mod n1 =", Decrypt(S1, private_B))
    print("7. Перевірка підпису (відкритий ключ A): k == S^e mod n")
    print("   Підпис вірний:", k_rec is not None)
    print("   Отриманий ключ збігається з надісланим:", k_rec == k)

    print("\n-----ПЕРЕВІРКА СПОТВОРЕННЯ ДАНИХ-----")
    print("Змінено S1 на одиницю -> результат ReceiveKey:",
          ReceiveKey(k1, (S1 + 1) % n1, private_B, public_A))
    print("Перевірка за чужим відкритим ключем (B замість A) -> результат ReceiveKey:",
          ReceiveKey(k1, S1, private_B, public_B))

    with open("rsa_task5_results.json", "w", encoding="utf-8") as f:
        json.dump({"k": k, "S": S, "k1": k1, "S1": S1, "k_received": k_rec}, f, indent=4)
    print("\nРезультати збережено у файл rsa_task5_results.json")
