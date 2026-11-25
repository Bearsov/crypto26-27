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

def h(x):                   # число -> hex
    s = format(x, "X")
    return "0" + s if len(s) % 2 else s


def from_h(s):              # hex -> число
    return int(s.strip(), 16)


# Мій ключ 
e = 65537
n = 6104886738324657918897358910357712048263984365444213457870760901724386711260194731146504967341897981850421186876489198599007767970269007124495879018516869
d = 4862428595355430042701424199486735908072260248284518642711687265347990630347172862079654530297350937007269951768894734008967692566752640675641531417652373

MSG = "0123456789ABCDEF"    # тестове повідомлення (hex)

print("Мій відкритий ключ:")
print("  Modulus         =", h(n))
print("  Public exponent =", h(e))
print("Тестове повідомлення MSG =", MSG)


# ===== Значення з сайту  =====

# Server Key 1024
SERVER_N = "B2B0029219C56CA8212EF88B7D21CEB234D1895B1CB551AC0A05CF5ACC0FF433ADC48DCC1B2D50DA325EF5986D6451ECCC46F67268E476BF173209E61734272DFF0C1A1A5A820903D528A00BF9DFD3D597B3336DD217D2EDE23212FCFAC9C63EA51B7F5C3A8C29B538CF3FB761A4BA51D8C6A518654151915AAFB6B0E580C495"           # Server Key -> Modulus
SERVER_E = "10001"

# Encryption
ENC_C = "524682B6C23A62DF7A4B5AA5919CB2D3B0268516DBB7D48B65477C0761D90E9A46F2964504439C4CAA0B544C0C03C56E3B9EB3653B3DD61C58E13D6108CEF55D"

#Signature
SIGN_S = "73FA7F42A83806ACA2A44BD37B2558EE398A72AE26C35FDDE048F6762388BEB05399CBEE8453B4DD66335A2CDDCAE635DC2816547E98D22EE30C697BBBC9AF7E754C776C05BD1E91AE3EC8753C095ECF5D04FDF1A499EF51F75611F221282BF6D4785B96234398273644099D5B93EDC97C38A68C37A737CD4E7EFACE642311EF"

# server key - 256
SERVER256_N = "C8CAFDC854195AC98B4028E0E956B278A24C88E84A07C540D76330426097A8E3"
SERVER256_E = "10001" 

# send key
SEND_K1 = "2AB82A920812449490C5810D3BD326DC52F112BDDE472B1CD90F3E99ABA57BC494FFA6D32466366918E2298C3C8040DA2A50E4EC250348A227C6EE2ED4BC6BF1"
SEND_S1 = "70004CCB35C3A21F66BB1BA7442309221F5560405CFB6060F432B1DAEBB8B8B7733C29D2B520070B98BE8864A0D15E180B89220822FBFD40BC15285CB80B340D"


# ===== Перевірки =====
M = from_h(MSG)

print("\n[Sign] мій підпис -> перевіряє сервер")
_, S = Sign(M, d, n)
print("  Message =", MSG, "| Signature =", h(S))

if ENC_C:
    print("\n[Decryption] сервер зашифрував MSG моїм ключем -> розшифровую я")
    M2 = Decrypt(from_h(ENC_C), d, n)
    print("  Decrypt(C) =", h(M2), "| збігається з MSG:", M2 == M)

if SERVER_N:
    n_s, e_s = from_h(SERVER_N), from_h(SERVER_E)

    print("\n[Encryption] я шифрую MSG ключем сервера -> розшифровує сервер")
    print("  Ciphertext =", h(Encrypt(M, e_s, n_s)))
    print("  сервер має показати: Message =", MSG)

    if SIGN_S:
        print("\n[Verify] сервер підписав MSG -> перевіряю я")
        print("  Verify(MSG, S) =", Verify(M, from_h(SIGN_S), e_s, n_s))

    print("\n[Receive Key] я надсилаю ключ серверу (SendKey у мене)")
    k = random.randrange(1, n)
    k1, S1 = SendKey(k, d, n, e_s, n_s, verbose=True)
    print("  Key =", h(k1))
    print("  Signature =", h(S1))
    print("  сервер має показати Key =", h(k))

if SERVER256_N and SEND_K1 and SEND_S1:
    print("\n[Send Key] сервер надіслав ключ мені (ReceiveKey у мене)")
    n_s, e_s = from_h(SERVER256_N), from_h(SERVER256_E)
    k = ReceiveKey(from_h(SEND_K1), from_h(SEND_S1), d, n, e_s, n_s, verbose=True)
    print("  отриманий ключ k =", "підпис НЕ пройшов перевірку" if k is None else h(k))
