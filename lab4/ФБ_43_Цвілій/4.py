import secrets

#  1. Математика 

def power_mod(b, e, m):
    """b^e mod m (схема Горнера)."""
    r = 1; b %= m
    while e:
        if e & 1: r = r * b % m
        b = b * b % m; e >>= 1 #степінь/2
    return r

def ext_gcd(a, b):
    if not b: return a, 1, 0
    g, x, y = ext_gcd(b, a % b)
    return g, y, x - (a // b) * y

def mod_inv(e, phi):
    g, x, _ = ext_gcd(e, phi)
    if g != 1: raise ValueError("Оберненого не існує")
    return x % phi

#  2. Тести простоти 

SMALL_PRIMES = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,
                73,79,83,89,97,101,103,107,109,113,127,131,137,139,149,151,
                157,163,167,173,179,181,191,193,197,199,211,223,227,229,233,
                239,241,251,257,263,269,271,277,281,283,293,307,311,313,317]

def trial_division(n):
    for p in SMALL_PRIMES:
        if n == p: return True
        if n % p == 0: return False
    return True

def miller_rabin(p, k=40):
    if p < 2: return False
    if p in (2, 3): return True
    if p % 2 == 0: return False
    d, s = p - 1, 0
    while d % 2 == 0: d //= 2; s += 1
    for _ in range(k):
        x = secrets.randbelow(p - 3) + 2 #рандом основа х
        xr = power_mod(x, d, p) #x^d mod p
        if xr in (1, p - 1): continue #yesss
        for _ in range(1, s):
            xr = xr * xr % p
            if xr == p - 1: break #yessss
            if xr == 1: return False
        else: return False
    return True

def miller_rabin_demo(p, base=2):
    """Проміжні результати одного раунду для звіту."""
    print(f"\n--- Тест Міллера-Рабіна за основою {base} ---")
    d, s = p - 1, 0
    while d % 2 == 0: d //= 2; s += 1
    print(f"p-1 = d·2^s  =>  d={d}, s={s}")
    xr = power_mod(base, d, p)
    print(f"Крок 2.1: x_0 = {base}^d mod p = {xr}")
    if xr in (1, p - 1):
        print(f"=> сильно псевдопросте (x_0 == {'1' if xr==1 else '-1'})")
        return
    for r in range(1, s):
        xr = xr * xr % p
        print(f"Крок 2.2 r={r}: x_{r} = {xr}")
        if xr == p - 1: print(f"=> сильно псевдопросте (x_{r} == -1)"); return
        if xr == 1:     print(f"=> СКЛАДЕНЕ (x_{r} == 1)"); return
    print("=> СКЛАДЕНЕ (жодного -1)")

#  3. Генерація простих чисел 

def get_prime(bits=256, rejected=None):
    while True:
        n = secrets.randbits(bits) | (1 << (bits - 1)) | 1 #перший біт одиниця + останній біт одиниця
        if not trial_division(n):
            if rejected is not None and len(rejected) < 5:
                rejected.append((n, "пробні ділення"))
            continue
        if not miller_rabin(n):
            if rejected is not None and len(rejected) < 5:
                rejected.append((n, "Міллер-Рабін"))
            continue
        return n

#  4. Обов'язкові процедури 

def GenerateKeyPair(bits=256, rejected=None):
    e = 65537
    while True:
        p = get_prime(bits, rejected)
        q = get_prime(bits, rejected)
        phi = (p - 1) * (q - 1)
        if p != q and ext_gcd(e, phi)[0] == 1:
            break
    n = p * q
    return (e, n), (mod_inv(e, phi), p, q)

def Encrypt(M, e, n):   return power_mod(M, e, n)
def Decrypt(C, d, n):   return power_mod(C, d, n)
def Sign(M, d, n):      return power_mod(M, d, n)
def Verify(M, S, e, n): return M == power_mod(S, e, n)

def SendKey(k, d_A, n_A, e_B, n_B):
    if n_A > n_B or not (0 < k < n_A):
        raise ValueError("Порушено умови протоколу")
    k_1 = Encrypt(k, e_B, n_B)
    S_1 = Encrypt(Sign(k, d_A, n_A), e_B, n_B)
    return k_1, S_1

def ReceiveKey(k_1, S_1, d_B, n_B, e_A, n_A):
    k = Decrypt(k_1, d_B, n_B)
    return k, Verify(k, Decrypt(S_1, d_B, n_B), e_A, n_A)



if __name__ == "__main__":
    SEP = "=" * 70

    # [1] Генерація простого числа + відхилені кандидати
    bad = []
    p_demo = get_prime(256, bad)
    print(SEP)
    print(f"[1] Просте p ({p_demo.bit_length()} біт):\n{hex(p_demo)}")
    print("Відхилені кандидати:")
    if not bad: print("  (немає — число знайдено з першої спроби)")
    for i, (c, r) in enumerate(bad, 1): print(f"  {i}. {hex(c)[:20]}... ({r})")
    miller_rabin_demo(p_demo, base=2)

   # [2] Генерація ключів A і B з умовою n_A <= n_B
    print(f"\n{SEP}\n[2] Генерація ключів RSA для A і B...")
    bad_A, bad_B = [], []
    pub_A, priv_A = GenerateKeyPair(256, bad_A)
    pub_B, priv_B = GenerateKeyPair(256, bad_B)

    if pub_A[1] > pub_B[1]:
        pub_A, priv_A, bad_A, pub_B, priv_B, bad_B = (
            pub_B,
            priv_B,
            bad_B,
            pub_A,
            priv_A,
            bad_A,
        )

    e_A, n_A = pub_A
    d_A, p_A, q_A = priv_A
    e_B, n_B = pub_B
    d_B, p_B, q_B = priv_B

    phi_A = (p_A - 1) * (q_A - 1)
    phi_B = (p_B - 1) * (q_B - 1)

    print("Абонент A:")
    print(f"  p  = {hex(p_A)}")
    print(f"  q  = {hex(q_A)}")
    print(f"  n  = {hex(n_A)}")
    print(f"  e  = {e_A}")
    print(f"  d  = {hex(d_A)}")
    print("  Відхилені кандидати при генерації для A:")
    for i, (c, r) in enumerate(bad_A, 1):
        print(f"    {i}. {hex(c)[:20]}... ({r})")

    print("\nАбонент B:")
    print(f"  p1 = {hex(p_B)}")
    print(f"  q1 = {hex(q_B)}")
    print(f"  n1 = {hex(n_B)}")
    print(f"  e1 = {e_B}")
    print(f"  d1 = {hex(d_B)}")
    print("  Відхилені кандидати при генерації для B:")
    for i, (c, r) in enumerate(bad_B, 1):
        print(f"    {i}. {hex(c)[:20]}... ({r})")

    print("\nПеревірки:")
    print(f"  n_A <= n_B: {n_A <= n_B}")
    print(f"  (e_A * d_A) mod phi_A == 1: {(e_A * d_A) % phi_A == 1}")
    print(f"  (e_B * d_B) mod phi_B == 1: {(e_B * d_B) % phi_B == 1}")

    # [3] Шифрування / розшифрування
    print(f"\n{SEP}\n[3] Шифрування і розшифрування...")
    M = secrets.randbelow(n_A - 1) + 1  

    # A шифрує для B
    C_forB = Encrypt(M, e_B, n_B)
    print(f"A -> B: M={hex(M)}\n  C={hex(C_forB)}\n  Розшифровано вірно: {Decrypt(C_forB, d_B, n_B) == M}")

    # B шифрує для A
    C_forA = Encrypt(M, e_A, n_A)
    print(f"B -> A: M={hex(M)}\n  C={hex(C_forA)}\n  Розшифровано вірно: {Decrypt(C_forA, d_A, n_A) == M}")

    # [4] Цифровий підпис
    print(f"\n{SEP}\n[4] Цифровий підпис...")
    S_A = Sign(M, d_A, n_A)
    print(f"Підпис A: S={hex(S_A)}\n  Вірний: {Verify(M, S_A, e_A, n_A)}")
    S_B = Sign(M, d_B, n_B)
    print(f"Підпис B: S={hex(S_B)}\n  Вірний: {Verify(M, S_B, e_B, n_B)}")

    # [5]  розсилання ключів A -> B
    print(f"\n{SEP}\n[5] Протокол розсилання ключів A -> B...")
    k = secrets.randbelow(n_A - 2) + 1
    k_1, S_1 = SendKey(k, d_A, n_A, e_B, n_B)
    k_recv, valid = ReceiveKey(k_1, S_1, d_B, n_B, e_A, n_A)
    print(f"k    = {hex(k)}")
    print(f"k_1  = {hex(k_1)}")
    print(f"S_1  = {hex(S_1)}")
    print(f"k отримано: {hex(k_recv)}")
    print(f"Ключі збігаються: {k == k_recv} | Підпис A підтверджено: {valid}")
    print(SEP)