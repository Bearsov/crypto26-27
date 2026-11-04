import random
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"
DATA = ROOT / "data"

E_DEFAULT = 2 ** 16 + 1
MR_ROUNDS = 40
PASCAL_BASE = 2 ** 16


def gcd(a, b):
    while b:
        a, b = b, a % b
    return a


def ext_gcd(a, b):
    old_r, r = a, b
    old_u, u = 1, 0
    old_v, v = 0, 1
    while r:
        q = old_r // r
        old_r, r = r, old_r - q * r
        old_u, u = u, old_u - q * u
        old_v, v = v, old_v - q * v
    return old_r, old_u, old_v


def mod_inverse(a, m):
    g, u, _ = ext_gcd(a % m, m)
    if g != 1:
        raise ValueError("елемент необоротний")
    return u % m


def mod_pow(x, alpha, m):
    y = 1
    for bit in bin(alpha)[2:]:
        y = y * y % m
        if bit == "1":
            y = y * x % m
    return y


def small_primes(limit=1000):
    sieve = [True] * limit
    result = []
    for i in range(2, limit):
        if sieve[i]:
            result.append(i)
            for j in range(i * i, limit, i):
                sieve[j] = False
    return result


SMALL_PRIMES = small_primes()


def pascal_divides(N, m, base=PASCAL_BASE):
    total, r = 0, 1
    while N:
        N, digit = divmod(N, base)
        total += digit * r
        r = r * base % m
    return total % m == 0


def trial_division(p):
    for m in SMALL_PRIMES:
        if p == m:
            return None
        if pascal_divides(p, m):
            return m
    return None


def decompose(p):
    d, s = p - 1, 0
    while d % 2 == 0:
        d //= 2
        s += 1
    return d, s


def strong_pseudoprime(p, x, d, s, trace=None):
    xr = mod_pow(x, d, p)
    if trace is not None:
        trace.append(("x^d", 0, xr))
    if xr == 1 or xr == p - 1:
        return True
    for r in range(1, s):
        xr = xr * xr % p
        if trace is not None:
            trace.append(("x^(d*2^r)", r, xr))
        if xr == p - 1:
            return True
        if xr == 1:
            return False
    return False


def miller_rabin(p, k=MR_ROUNDS, rng=random, traces=None):
    if p < 2:
        return False, None
    if p in (2, 3):
        return True, None
    if p % 2 == 0:
        return False, 2
    d, s = decompose(p)
    for _ in range(k):
        x = rng.randrange(2, p - 1)
        if gcd(x, p) != 1:
            return False, x
        trace = [] if traces is not None else None
        passed = strong_pseudoprime(p, x, d, s, trace)
        if traces is not None:
            traces.append({"x": x, "d": d, "s": s, "steps": trace, "passed": passed})
        if not passed:
            return False, x
    return True, None


def is_prime(p, k=MR_ROUNDS, rng=random):
    if p < 2 or trial_division(p) is not None:
        return False
    return miller_rabin(p, k, rng)[0]


@dataclass
class PrimeSearch:
    p: int
    x: int
    m0: int
    rejected_trial: list = field(default_factory=list)
    rejected_mr: list = field(default_factory=list)
    traces: list = field(default_factory=list)


def random_prime(n0, n1, k=MR_ROUNDS, rng=random):
    while True:
        x = rng.randint(n0, n1)
        m0 = x if x % 2 else x + 1
        search = PrimeSearch(0, x, m0)
        for i in range((n1 - m0) // 2 + 1):
            candidate = m0 + 2 * i
            divisor = trial_division(candidate)
            if divisor is not None:
                search.rejected_trial.append((i, candidate, divisor))
                continue
            traces = []
            prime, witness = miller_rabin(candidate, k, rng, traces)
            if not prime:
                search.rejected_mr.append((i, candidate, witness, traces[-1] if traces else None))
                continue
            search.p = candidate
            search.traces = traces
            return search


def random_prime_bits(bits, k=MR_ROUNDS, rng=random):
    return random_prime(2 ** (bits - 1), 2 ** bits - 1, k, rng)


@dataclass
class PublicKey:
    n: int
    e: int


@dataclass
class PrivateKey:
    d: int
    p: int
    q: int


def GenerateKeyPair(p, q, e=E_DEFAULT):
    if p == q:
        raise ValueError("p і q мають бути різними")
    phi = (p - 1) * (q - 1)
    if not 2 <= e <= phi - 1 or gcd(e, phi) != 1:
        raise ValueError("e не взаємно просте з phi(n)")
    return PublicKey(p * q, e), PrivateKey(mod_inverse(e, phi), p, q)


def Encrypt(M, e, n):
    if not 0 <= M < n:
        raise ValueError("M поза діапазоном [0, n-1]")
    return mod_pow(M, e, n)


def Decrypt(C, d, n):
    if not 0 <= C < n:
        raise ValueError("C поза діапазоном [0, n-1]")
    return mod_pow(C, d, n)


def Sign(M, d, n):
    if not 0 <= M < n:
        raise ValueError("M поза діапазоном [0, n-1]")
    return mod_pow(M, d, n)


def Verify(M, S, e, n):
    if not (0 <= M < n and 0 <= S < n):
        return False
    return mod_pow(S, e, n) == M


def SendKey(k, d, n, e1, n1):
    if n1 < n:
        raise ValueError("потрібно n1 >= n: відправник має згенерувати інші ключі")
    if not 0 < k < n:
        raise ValueError("k поза діапазоном (0, n)")
    S = Sign(k, d, n)
    return Encrypt(k, e1, n1), Encrypt(S, e1, n1)


def ReceiveKey(k1, S1, d1, n1, e, n):
    k = Decrypt(k1, d1, n1)
    S = Decrypt(S1, d1, n1)
    return k, 0 < k < n and Verify(k, S, e, n)
