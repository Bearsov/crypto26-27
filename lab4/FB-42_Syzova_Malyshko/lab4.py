import random
import sys

SMALL_PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47,
                53, 59, 61, 67, 71, 73, 79, 83, 89, 97]

# Завдання 1. Допоміжна арифметика 

def gcd(a, b):
    while b:
        a, b = b, a % b
    return a

def egcd(a, b):
    x0, y0, x1, y1 = 1, 0, 0, 1
    while b:
        q = a // b
        a, b = b, a - q * b
        x0, x1 = x1, x0 - q * x1
        y0, y1 = y1, y0 - q * y1
    return a, x0, y0

def mod_inverse(a, m):
    g, x, _ = egcd(a, m)
    if g != 1:
        raise ValueError("Оберненого елемента не існує")
    return x % m

def mod_pow(x, a, m):
    y = 1
    for bit in bin(a)[2:]:
        y = y * y % m
        if bit == '1':
            y = y * x % m
    return y

# Завдання 2. Тести на простоту та генерація чисел 

def decompose(p):
    d, s = p - 1, 0
    while d % 2 == 0:
        d //= 2
        s += 1
    return d, s

def strong_pseudoprime(p, a, trace=None):
    d, s = decompose(p)
    x = mod_pow(a, d, p)
    if trace is not None:
        trace.append((0, x))
    if x == 1 or x == p - 1:
        return True
    for r in range(1, s):
        x = x * x % p
        if trace is not None:
            trace.append((r, x))
        if x == p - 1:
            return True
        if x == 1:
            return False
    return False

def is_probable_prime(p, k=20):
    if p < 2:
        return False, "p < 2"
    for q in SMALL_PRIMES:
        if p == q:
            return True, "Мале просте"
        if p % q == 0:
            return False, f"Ділиться на {q}"
    for _ in range(k):
        a = random.randint(2, p - 2)
        if gcd(a, p) != 1:
            return False, f"gcd(a, p) != 1"
        if not strong_pseudoprime(p, a):
            return False, "Не пройшло тест Міллера-Рабіна"
    return True, "Пройшло тести"

def gen_prime_interval(n0, n1, k=20, log=None):
    while True:
        x = random.randint(n0, n1)
        m = x if x % 2 == 1 else x + 1
        while m <= n1:
            ok, reason = is_probable_prime(m, k)
            if ok:
                return m
            if log is not None:
                log.append((m, reason))
            m += 2

def gen_prime(bits, k=20, log=None):
    return gen_prime_interval(1 << (bits - 1), (1 << bits) - 1, k, log)

def gen_safe_prime(bits, k=20, log=None):
    while True:
        p_prime = gen_prime(bits - 1, k, None)
        p = 2 * p_prime + 1
        ok, reason = is_probable_prime(p, k)
        if ok:
            return p
        if log is not None:
            log.append((p, f"Відхилено: {reason}"))

def miller_rabin_report(p, a):
    d, s = decompose(p)
    trace = []
    res = strong_pseudoprime(p, a, trace)
    print(f"p = {p}\np-1 = d * 2^s (s={s}, d={d})\nОснова a = {a}")
    for r, x in trace:
        print(f"x_{r} = {x}")
    print("Висновок: p псевдопросте" if res else "Висновок: p складене")


# Завдання 3. Побудова криптосистеми RSA 

def GenerateKeyPair(p, q, e=65537):
    if p == q:
        raise ValueError("p і q однакові")
    n = p * q
    phi = (p - 1) * (q - 1)
    if not (1 < e < phi and gcd(e, phi) == 1):
        while True:
            e = random.randrange(3, phi - 1, 2)
            if gcd(e, phi) == 1:
                break
    d = mod_inverse(e, phi)
    return (n, e), (d, p, q)


# Завдання 4. Шифрування, підпис та протокол розсилання

def Encrypt(M, e, n):
    return mod_pow(M, e, n)

def Decrypt(C, d, n):
    return mod_pow(C, d, n)

def Sign(M, d, n):
    return mod_pow(M, d, n)

def Verify(M, S, e, n):
    return mod_pow(S, e, n) == M

def SendKey(k, d_A, n_A, e_B, n_B):
    S = Sign(k, d_A, n_A)
    k1 = Encrypt(k, e_B, n_B)
    S1 = Encrypt(S, e_B, n_B)
    return k1, S1

def ReceiveKey(k1, S1, d_B, n_B, e_A, n_A):
    k = Decrypt(k1, d_B, n_B)
    S = Decrypt(S1, d_B, n_B)
    if not Verify(k, S, e_A, n_A):
        raise ValueError("Підпис відправника не підтверджено")
    return k

def hx(x):
    return hex(x)


# Демонстрація виконання

def main():
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else None
    random.seed(seed)
    BITS, K = 256, 20

    print("\n Завдання 2: Генерація безпечних простих чисел")
    primes, logs = {}, {}
    for name in ("p", "q", "p1", "q1"):
        logs[name] = []
        primes[name] = gen_safe_prime(BITS, K, logs[name])
    p, q, p1, q1 = primes["p"], primes["q"], primes["p1"], primes["q1"]
    
    if p * q > p1 * q1:
        p, q, p1, q1 = p1, q1, p, q
        
    print(f"p = {p}\nq = {q}\np1 = {p1}\nq1 = {q1}")

    print("\n Завдання 3: Генерація ключів RSA")
    pubA, privA = GenerateKeyPair(p, q)
    pubB, privB = GenerateKeyPair(p1, q1)
    nA, eA = pubA; dA = privA[0]
    nB, eB = pubB; dB = privB[0]
    
    print(f"Абонент A:\n  n = {hx(nA)}\n  e = {eA}\n  d = {hx(dA)}")
    print(f"Абонент B:\n  n = {hx(nB)}\n  e = {eB}\n  d = {hx(dB)}")

    print("\n Завдання 4: Підпис та протокол розсилання ключів")
    M = random.randint(2, nA - 1)
    C = Encrypt(M, eA, nA)
    S = Sign(M, dA, nA)
    print(f"Повідомлення M: {hx(M)}\nЗашифроване C: {hx(C)}\nПідпис S: {hx(S)}")
    print(f"Перевірка підпису: {Verify(M, S, eA, nA)}")

    k = random.randint(1, nA - 1)
    print(f"\nВідправка секрету k: {hx(k)}")
    k1, S1 = SendKey(k, dA, nA, eB, nB)
    k_rec = ReceiveKey(k1, S1, dB, nB, eA, nA)
    print(f"Отриманий абонентом B секрет: {hx(k_rec)}")
    print(f"k_A == k_B: {k == k_rec}")

if __name__ == "__main__":
    main()