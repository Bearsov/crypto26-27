import random

SMALL_PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47] # перші 15 простих чисел

# ---------- Завдання 1 ----------

def gcd(a, b): # НСД
    while b:
        a, b = b, a % b
    return a


def mod_pow(x, a, m): # x^a mod m - схема Горнера
    y = 1
    for bit in bin(a)[2:]:
        y = y * y % m
        if bit == "1":
            y = y * x % m
    return y


def is_strong_pseudoprime(p, x, verbose=False):  # Крок 2 тесту Міллера-Рабіна для основи x
    d, s = p - 1, 0
    while d % 2 == 0:
        d //= 2
        s += 1
    xr = mod_pow(x, d, p)
    if verbose:
        print(f"  p - 1 = d * 2^s, s = {s}, d = {d}")
        print(f"  x = {x}")
        print(f"  x_0 = x^d mod p = {xr}")
    if xr == 1 or xr == p - 1:
        return True
    for r in range(1, s):
        xr = xr * xr % p
        if verbose:
            print(f"  x_{r} = {xr}")
        if xr == p - 1:
            return True
        if xr == 1:
            return False
    return False


def is_prime(p, k=40): # задля пришвидшення роботи - пробні ділення на 15 найменших простих чисел, 
                       # а вже після цього тест Міллера-Рабіна з k основами (значно дорожчий по ресурсам)
    for sp in SMALL_PRIMES:
        if p % sp == 0:
            return p == sp
    for _ in range(k):
        x = random.randrange(2, p - 1)
        if gcd(x, p) > 1 or not is_strong_pseudoprime(p, x):
            return False
    return True


def random_prime(bits): # генерація випадкового простого числа з bits бітів
    rejected = []
    while True:
        m = random.getrandbits(bits) | (1 << (bits - 1)) | 1
        while m.bit_length() == bits:
            if is_prime(m):
                return m, rejected
            rejected.append(m)
            m += 2


# ---------- Завдання 2 ----------

def generate_prime_pairs(bits=256): # генерує дві пари простих
    primes = [random_prime(bits) for _ in range(4)]
    pair_a, pair_b = primes[:2], primes[2:]
    if pair_a[0][0] * pair_a[1][0] > pair_b[0][0] * pair_b[1][0]:
        pair_a, pair_b = pair_b, pair_a               # міняємо місцями за потреби, щоб pq <= p1q1
    return pair_a, pair_b


# ---------- Завдання 3 ----------

def mod_inverse(a, m): # пошук оберненого елемента - a^-1 mod m (розширений алгоритм Евкліда)
    r0, r1 = m, a % m
    t0, t1 = 0, 1
    while r1:
        q = r0 // r1
        r0, r1 = r1, r0 - q * r1
        t0, t1 = t1, t0 - q * t1
    if r0 != 1:
        raise ValueError("оберненого елемента не існує")
    return t0 % m


def GenerateKeyPair(p, q):                 # повертає відкритий ключ (e, n) і секретний ключ (d, p, q)
    n = p * q
    phi = (p - 1) * (q - 1)
    e = 2 ** 16 + 1
    while gcd(e, phi) != 1:                # якщо 2^16+1 не підходить - беремо випадкове e
        e = random.randrange(2, phi - 1)
    d = mod_inverse(e, phi)
    return (e, n), (d, p, q)


# ---------- Завдання 4 ----------

def Encrypt(M, e, n):       # шифрування відкритим ключем адресата: C = M^e mod n
    return mod_pow(M, e, n)


def Decrypt(C, d, n):       # розшифрування своїм секретним ключем: M = C^d mod n
    return mod_pow(C, d, n)


def Sign(M, d, n):          # підпис своїм секретним ключем: S = M^d mod n, повідомлення з підписом - (M, S)
    return M, mod_pow(M, d, n)


def Verify(M, S, e, n):     # перевірка підпису відкритим ключем автора: M == S^e mod n
    return mod_pow(S, e, n) == M


# ---------- Завдання 5 ----------
#     ПРИМЕР ПЕРЕДАЧИ
#    / открытый / закрытый
# Я  / огурец  / помидор
#    /         /
# Ты / яблоко  / вишня

# лимон
# 48192 Підпис мой (лимон + помидор)
# 62357 (лимон + яблоко) 90512 (48192 + яблоко)
# лимон (62357 + вишня) 48192 (90512 + вишня)
# лимон (48192 + огурец)

def SendKey(k, d, n, e1, n1, verbose=False):   # A: свій секретий ключ (d, n) + відкритий ключ B (e1, n1)
    if n1 < n:
        raise ValueError("n1 < n: абонент A повинен згенерувати іншу пару ключів")
    _, S = Sign(k, d, n)            # S  = k^d mod n    - підпис A (автентичність)
    k1 = Encrypt(k, e1, n1)         # k1 = k^e1 mod n1  - ключ, зашифрований для B (конфіденційність)
    S1 = Encrypt(S, e1, n1)         # S1 = S^e1 mod n1  - підпис, зашифрований для B
    if verbose:
        print("  A: S  = k^d mod n   =", S)
        print("  A: k1 = k^e1 mod n1 =", k1)
        print("  A: S1 = S^e1 mod n1 =", S1)
    return k1, S1                   # повідомлення (k1, S1), яке A відправляє B


def ReceiveKey(k1, S1, d1, n1, e, n, verbose=False):   # B: свій секретний ключ (d1, n1) + відкритий ключ A (e, n)
    k = Decrypt(k1, d1, n1)         # k = k1^d1 mod n1
    S = Decrypt(S1, d1, n1)         # S = S1^d1 mod n1
    ok = Verify(k, S, e, n)         # k == S^e mod n ?
    if verbose:
        print("  B: k  = k1^d1 mod n1 =", k)
        print("  B: S  = S1^d1 mod n1 =", S)
        print("  B: S^e mod n = k:", ok)
    return k if ok else None        # None - якщо підпис не пройшов перевірку, ключ відкидається


# ---------- main ----------

print("Завдання 1")
p, rejected = random_prime(256)
print("p =", p)
print(f"Відкинуті кандидати ({len(rejected)}):")
for m in rejected:
    print(" ", m)
print("Міллер-Рабін для p:")
ok = is_strong_pseudoprime(p, random.randrange(2, p - 1), verbose=True)
print("  результат:", "пройдено" if ok else "не пройдено")

print("\nЗавдання 2")
(p_a, q_a), (p_b, q_b) = generate_prime_pairs(256)
for name, (prime, rej) in [("p", p_a), ("q", q_a), ("p1", p_b), ("q1", q_b)]:
    print(f"{name} = {prime}")

p, q, p1, q1 = p_a[0], q_a[0], p_b[0], q_b[0]    # секрені прості числа абонентів
print("pq <= p1q1:", p * q <= p1 * q1)

print("\nЗавдання 3")
pub_a, priv_a = GenerateKeyPair(p, q)      # абонент A: (e, n), (d, p, q)
pub_b, priv_b = GenerateKeyPair(p1, q1)    # абонент B: (e1, n1), (d1, p1, q1)
e, n = pub_a    # e=2^16+1  n=p*q
d = priv_a[0]
e1, n1 = pub_b
d1 = priv_b[0]
print("Абонент A:")
print("  e =", e)
print("  n =", n)
print("  d =", d)
print("Абонент B:")
print("  e1 =", e1)
print("  n1 =", n1)
print("  d1 =", d1)

print("Перевірка співвідношень для ключів A:")
phi = (p - 1) * (q - 1)
print("  phi(n) = (p-1)(q-1) =", phi)
print("  n = p*q:", n == p * q)
print("  1 < e < phi(n):", 1 < e < phi)
print("  gcd(e, phi(n)) = 1:", gcd(e, phi) == 1)
print("  e*d mod phi(n) = 1:", e * d % phi == 1)
M = random.randrange(0, n)
print("  (M^e)^d mod n = M:", mod_pow(mod_pow(M, e, n), d, n) == M)

print("\nЗавдання 4")
for name, (e_x, n_x), d_x in [("A", (e, n), d), ("B", (e1, n1), d1)]:
    print(f"Абонент {name}:")
    M = random.randrange(0, n_x)              # випадкове відкрите повідомлення, 0 <= M < n
    C = Encrypt(M, e_x, n_x)                  # хтось шифрує для абонента його відкритим ключем
    M2 = Decrypt(C, d_x, n_x)                 # абонент розшифровує своїм секретним ключем
    print("  M  =", M)
    print("  C  =", C)
    print("  Decrypt(C) =", M2)
    print("  розшифрування правильне:", M2 == M)

    M, S = Sign(M, d_x, n_x)                  # абонент підписує M своїм секретним ключем
    print("  підпис S =", S)
    print("  Verify(M, S):", Verify(M, S, e_x, n_x))
    print("  Verify(M+1, S) (спотворене повідомлення):", Verify(M + 1, S, e_x, n_x))

print("\nЗавдання 5")
k = random.randrange(1, n)                                 # секретний ключ для передачі, 0 < k < n
print("A хоче передати k =", k)
k1, S1 = SendKey(k, d, n, e1, n1, verbose=True)           # A -> B: (k1, S1) по відкритому каналу
print("Передано по каналу: (k1, S1)")
k_received = ReceiveKey(k1, S1, d1, n1, e, n, verbose=True)
print("B отримав k =", k_received)
print("ключ збігається:", k_received == k)