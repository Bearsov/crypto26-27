
import random
import os
from pathlib import Path
from math import gcd

# True - використовувати збережені результати
# False - згенерувати нові результати
os.chdir(Path(__file__).resolve().parent)
REUSE_SAVED = True

def trial_division(n):
    primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37]
    for p in primes:
        if n == p:
            return True
        if n % p == 0:
            return False
    return True

def modular_power(x, a, m):
    y = 1
    for bit in bin(a)[2:]:
        y = (y * y) % m
        if bit == "1":
            y = (y * x) % m
    return y

def miller_rabin(n, k=40, details=False, first_base=None):
    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0:
        return False
    if not trial_division(n):
        return False
    d = n - 1
    s = 0
    while d % 2 == 0:
        d //= 2
        s += 1
    if details:
        print("n =", n)
        print("n - 1 = d * 2^s")
        print("d =", d)
        print("s =", s)
    for i in range(k):
        if i == 0 and first_base is not None:
            x = first_base
        else:
            x = random.randrange(2, n - 1)
        if gcd(x, n) != 1:
            return False
        y = modular_power(x, d, n)
        if details and i == 0:
            print("\nОснова x =", x)
            print("gcd(x, n) =", gcd(x, n))
            print("x^d mod n =", y)
        if y == 1 or y == n - 1:
            if details and i == 0:
                print("Перевірку за цією основою пройдено")
            continue
        passed = False
        for r in range(1, s):
            y = (y * y) % n
            if details and i == 0:
                print("r =", r)
                print("x^(d*2^r) mod n =", y)
            if y == n - 1:
                passed = True
                break
            if y == 1:
                return False
        if not passed:
            return False
    return True

def generate_prime(bits=256):
    if bits < 2:
        raise ValueError("Мінімальна довжина — 2 біти")
    rejected = []
    while True:
        n = random.getrandbits(bits)
        n |= (1 << (bits - 1))
        n |= 1
        if miller_rabin(n):
            return n, rejected
        rejected.append(n)


print("\n\n                     -----ЗАВДАННЯ 1. ГЕНЕРАЦІЯ ПРОСТОГО ЧИСЛА-----")
if REUSE_SAVED:
    p = 114748244092229380762366815568789224862795043789438702471323580367482101979953
    # Перші 5 відхилених кандидатів попереднього запуску
    rejected = [
        64542143141296693194293968898407264369288607963385764043429257489177102727429,
        111933990147150365931480689190439442730063801588102344736926926258757840992151,
        64705207134021192859333089499515320803659932154269921209133214666807416098183,
        103578512932916690312165326699852948708011103948546871566176696173965872796693,
        113949249562609406470787931098982376677325069273027232439652343947668206693793
    ]
    rejected_count = 62
else:
    p, rejected = generate_prime(256)
    rejected_count = len(rejected)
print("\nЗгенероване просте число:")
print("p =", p)
print("\nБітова довжина:")
print(p.bit_length(), "біт")
print("\nКількість відхилених кандидатів:")
print(rejected_count)
print("\nПерші 5 відхилених кандидатів:")
for i, n in enumerate(rejected[:5], 1):
    print(i, "-", n)
print("\nПеревірка тестом Міллера-Рабіна:")

if REUSE_SAVED:
    first_base = 67586133465845952094899344662404381718835308685523109680699619539592065806439
else:
    first_base = None
result = miller_rabin(p, 40, True, first_base)
print("\nПідсумковий результат:")
print("Число пройшло тест:", result)



print("\n\n                         -----ЗАВДАННЯ 2. ГЕНЕРАЦІЯ ПАР ПРОСТИХ ЧИСЕЛ-----")

p = 114748244092229380762366815568789224862795043789438702471323580367482101979953

if REUSE_SAVED:
    primes_saved = {}
    with open("rsa_primes.txt", "r", encoding="utf-8") as f:
        for line in f:
            if "=" in line:
                name, value = line.strip().split("=", 1)
                primes_saved[name.strip()] = int(value.strip())
    p = primes_saved["p"]
    q = primes_saved["q"]
    p1 = primes_saved["p1"]
    q1 = primes_saved["q1"]
    rejected_counts = {}
    with open("rejected_candidates.txt", "r", encoding="utf-8") as f:
        for line in f:
            if ":" in line and "відхилених" in line:
                name, value = line.split(":", 1)
                rejected_counts[name.strip()] = int(value.strip().split()[0])
    n = p * q
    n1 = p1 * q1

    if n != primes_saved["n"] or n1 != primes_saved["n1"] or n > n1:
        raise ValueError("Збережені параметри RSA не узгоджені")
else:
    q, rejected_q = generate_prime(256)
    p1, rejected_p1 = generate_prime(256)
    q1, rejected_q1 = generate_prime(256)
    n = p * q
    n1 = p1 * q1
    
    while n1 < n or p1 == q1:
        p1, rejected_new_p1 = generate_prime(256)
        q1, rejected_new_q1 = generate_prime(256)
        rejected_p1.extend(rejected_new_p1)
        rejected_q1.extend(rejected_new_q1)
        n1 = p1 * q1
    rejected_counts = {
        "q": len(rejected_q),
        "p1": len(rejected_p1),
        "q1": len(rejected_q1)
    }

print("\nАбонент A:")
print("p =", p)
print("q =", q)

print("\nАбонент B:")
print("p1 =", p1)
print("q1 =", q1)

print("\nБітові довжини:")
print("p:", p.bit_length())
print("q:", q.bit_length())
print("p1:", p1.bit_length())
print("q1:", q1.bit_length())

print("\nДобутки простих чисел:")
print("n = p * q =", n)
print("n1 = p1 * q1 =", n1)

print("\nПеревірка умови p*q <= p1*q1:")
print(n <= n1)

print("\nПеревірка простоти:")
print("p:", miller_rabin(p))
print("q:", miller_rabin(q))
print("p1:", miller_rabin(p1))
print("q1:", miller_rabin(q1))

print("\nКількість відхилених кандидатів:")
print("q:", rejected_counts["q"])
print("p1:", rejected_counts["p1"])
print("q1:", rejected_counts["q1"])

if not REUSE_SAVED:
    with open("rsa_primes.txt", "w", encoding="utf-8") as f:
        f.write(f"p = {p}\n")
        f.write(f"q = {q}\n")
        f.write(f"p1 = {p1}\n")
        f.write(f"q1 = {q1}\n")
        f.write(f"n = {n}\n")
        f.write(f"n1 = {n1}\n")
    with open("rejected_candidates.txt", "w", encoding="utf-8") as f:
        for name, candidates in [
            ("q", rejected_q),
            ("p1", rejected_p1),
            ("q1", rejected_q1)
        ]:
            f.write(f"\n{name}: {len(candidates)} відхилених кандидатів\n")
            for candidate in candidates:
                f.write(f"{candidate}\n")

print("\nРезультати збережено у файли:")
print("rsa_primes.txt")
print("rejected_candidates.txt")



import random
import json
from math import gcd

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
    public_key = (n, e)
    private_key = (d, p, q)
    return public_key, private_key

def read_primes(filename):
    values = {}
    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            if "=" in line:
                name, value = line.strip().split("=", 1)
                values[name.strip()] = int(value.strip())
    return values

primes = read_primes("rsa_primes.txt")
p = primes["p"]
q = primes["q"]
p1 = primes["p1"]
q1 = primes["q1"]
public_A, private_A = GenerateKeyPair(p, q)
public_B, private_B = GenerateKeyPair(p1, q1)
n, e = public_A
d, _, _ = private_A
n1, e1 = public_B
d1, _, _ = private_B

phi_A = (p - 1) * (q - 1)
phi_B = (p1 - 1) * (q1 - 1)

print("\n\n                       -----ЗАВДАННЯ 3. ГЕНЕРАЦІЯ КЛЮЧІВ RSA-----")

print("\nАбонент A:")
print("n =", n)
print("phi(n) =", phi_A)
print("e =", e)
print("d =", d)

print("\nАбонент B:")
print("n1 =", n1)
print("phi(n1) =", phi_B)
print("e1 =", e1)
print("d1 =", d1)

print("\nПеревірка параметрів RSA для абонента A:")
print("n = p*q:", n == p * q)
print("phi(n) = (p-1)*(q-1):", phi_A == (p - 1) * (q - 1))
print("2 <= e <= phi(n)-1:", 2 <= e <= phi_A - 1)
print("gcd(e, phi(n)) =", gcd(e, phi_A))
print("e*d mod phi(n) =", (e * d) % phi_A)

print("\nПеревірка параметрів RSA для абонента B:")
print("n1 = p1*q1:", n1 == p1 * q1)
print("2 <= e1 <= phi(n1)-1:", 2 <= e1 <= phi_B - 1)
print("gcd(e1, phi(n1)) =", gcd(e1, phi_B))
print("e1*d1 mod phi(n1) =", (e1 * d1) % phi_B)

print("\nПеревірка умови n <= n1:")
print(n <= n1)

keys = {
    "A": {
        "public": {"n": n, "e": e},
        "private": {"d": d, "p": p, "q": q}
    },
    "B": {
        "public": {"n": n1, "e": e1},
        "private": {"d": d1, "p": p1, "q": q1}
    }
}

if REUSE_SAVED:
    with open("rsa_keys.json", "r", encoding="utf-8") as f:
        saved_keys = json.load(f)
    if keys != saved_keys:
        raise ValueError("Збережені ключі не відповідають простим числам")
else:
    with open("rsa_keys.json", "w", encoding="utf-8") as f:
        json.dump(keys, f, indent=4)

print("\nКлючові пари збережено у файл rsa_keys.json")





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
    if not 0 <= message < n:
        return False
    if not 0 <= signature < n:
        return False
    recovered = pow(signature, e, n)
    return recovered == message

with open("rsa_keys.json", "r", encoding="utf-8") as f:
    keys = json.load(f)

public_A = (keys["A"]["public"]["n"], keys["A"]["public"]["e"])
private_A = (keys["A"]["private"]["d"], keys["A"]["private"]["p"], keys["A"]["private"]["q"])
public_B = (keys["B"]["public"]["n"], keys["B"]["public"]["e"])
private_B = (keys["B"]["private"]["d"], keys["B"]["private"]["p"], keys["B"]["private"]["q"])



print("\n\n                                  -----ЗАВДАННЯ 4. ШИФРУВАННЯ ТА ЦИФРОВИЙ ПІДПИС RSA-----")
if REUSE_SAVED:
    with open("rsa_task4_results.json", "r", encoding="utf-8") as f:
        saved_results = json.load(f)
    message_A = saved_results["A"]["message"]
    message_B = saved_results["B"]["message"]
else:
    message_A = random.randrange(1, public_A[0])
    message_B = random.randrange(1, public_B[0])

print("\n-----АБОНЕНТ A-----")
cipher_A = Encrypt(message_A, public_A)
decrypted_A = Decrypt(cipher_A, private_A)
signature_A = Sign(message_A, private_A)
verified_A = Verify(message_A, signature_A, public_A)
print("Відкрите повідомлення M =", message_A)
print("Криптограма C =", cipher_A)
print("Розшифроване повідомлення =", decrypted_A)
print("Правильність розшифрування:", message_A == decrypted_A)
print("\nЦифровий підпис S =", signature_A)
print("Перевірка підпису:", verified_A)

print("\n-----АБОНЕНТ B-----")
cipher_B = Encrypt(message_B, public_B)
decrypted_B = Decrypt(cipher_B, private_B)
signature_B = Sign(message_B, private_B)
verified_B = Verify(message_B, signature_B, public_B)
print("Відкрите повідомлення M =", message_B)
print("Криптограма C =", cipher_B)
print("Розшифроване повідомлення =", decrypted_B)
print("Правильність розшифрування:", message_B == decrypted_B)
print("\nЦифровий підпис S =", signature_B)
print("Перевірка підпису:", verified_B)

print("\n-----ПЕРЕВІРКА ЗМІНЕНОГО ПОВІДОМЛЕННЯ-----")
modified_message = (message_A + 1) % public_A[0]
print("Початкове повідомлення =", message_A)
print("Змінене повідомлення =", modified_message)
print(
    "Перевірка підпису зміненого повідомлення:",
    Verify(modified_message, signature_A, public_A)
)

results = {
    "A": {
        "message": message_A,
        "ciphertext": cipher_A,
        "decrypted": decrypted_A,
        "signature": signature_A,
        "verified": verified_A
    },
    "B": {
        "message": message_B,
        "ciphertext": cipher_B,
        "decrypted": decrypted_B,
        "signature": signature_B,
        "verified": verified_B
    }
}

if REUSE_SAVED:
    if results != saved_results:
        raise ValueError("Результати завдання 4 не відповідають збереженим даним")
else:
    with open("rsa_task4_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4)

print("\nРезультати збережено у файл rsa_task4_results.json")
