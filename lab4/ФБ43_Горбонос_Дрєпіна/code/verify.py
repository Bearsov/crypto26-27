import json
import random

from sympy import isprime

from rsa import (RESULTS, Decrypt, Encrypt, GenerateKeyPair, ReceiveKey, SendKey, Sign, Verify,
                 ext_gcd, gcd, miller_rabin, mod_inverse, mod_pow, pascal_divides, small_primes,
                 strong_pseudoprime, decompose, trial_division, is_prime)

failures = []


def check(name, condition):
    print(("OK   " if condition else "FAIL ") + name)
    if not condition:
        failures.append(name)


rng = random.Random(1)

check("mod_pow збігається з pow",
      all(mod_pow(a, b, m) == pow(a, b, m)
          for a, b, m in ((rng.getrandbits(512), rng.getrandbits(512), rng.getrandbits(512) | 1) for _ in range(200))))
check("gcd збігається з ext_gcd і тотожність Безу", all(
    (lambda a, b, r: r[0] == gcd(a, b) and a * r[1] + b * r[2] == r[0])(a, b, ext_gcd(a, b))
    for a, b in ((rng.getrandbits(256), rng.getrandbits(256)) for _ in range(200))))
check("mod_inverse збігається з pow(a, -1, m)", all(
    mod_inverse(a, 2 ** 256 + 297) == pow(a, -1, 2 ** 256 + 297)
    for a in (rng.getrandbits(255) * 2 + 1 for _ in range(100)) if gcd(a, 2 ** 256 + 297) == 1))
check("ознака Паскаля збігається з %", all(
    pascal_divides(n, m) == (n % m == 0)
    for n in (rng.getrandbits(512) for _ in range(30)) for m in small_primes(200)))
check("is_prime збігається з sympy для всіх чисел до 20000", all(
    is_prime(n, 20, rng) == isprime(n) for n in range(2, 20000)))
check("Кармайклові числа визнано складеними",
      not any(is_prime(n, 20, rng) for n in (561, 1105, 1729, 2465, 2821, 6601, 8911, 41041, 825265)))
d, s = decompose(2047)
check("2047 сильно псевдопросте за основою 2, але складене",
      strong_pseudoprime(2047, 2, d, s) and not miller_rabin(2047, 20, rng)[0])
check("великі складені добутки відкидаються", not is_prime((2 ** 127 - 1) * (2 ** 89 - 1), 20, rng))
check("просте 2^521-1 приймається", is_prime(2 ** 521 - 1, 20, rng))
check("trial_division не відкидає малі прості", trial_division(997) is None and trial_division(991) is None)

primes = json.loads((RESULTS / "primes.json").read_text("utf-8"))
values = {n: int(i["p"], 16) for n, i in primes["primes"].items()}
check("p, q, p1, q1 прості за sympy", all(isprime(v) for v in values.values()))
check("усі чотири простих мають 256 біт", all(v.bit_length() == 256 for v in values.values()))
check("pq <= p1q1", values["p"] * values["q"] <= values["p1"] * values["q1"])
check("усі відкинуті кандидати справді складені", all(
    not isprime(int(c["candidate"], 16))
    for i in primes["primes"].values() for c in i["rejected_trial"] + i["rejected_mr"]))
check("дільники пробних ділень правильні", all(
    int(c["candidate"], 16) % c["divisor"] == 0 for i in primes["primes"].values() for c in i["rejected_trial"]))
check("кандидати йдуть як m0 + 2i", all(
    int(c["candidate"], 16) == int(i["m0"], 16) + 2 * c["i"]
    for i in primes["primes"].values() for c in i["rejected_trial"] + i["rejected_mr"]))
check("свідки Міллера-Рабіна справді спростовують простоту", all(
    (lambda n, w: not strong_pseudoprime(n, w, *decompose(n)))(int(c["candidate"], 16), int(c["witness"], 16))
    for i in primes["primes"].values() for c in i["rejected_mr"]))

keys = json.loads((RESULTS / "keys.json").read_text("utf-8"))
for who, (p, q) in {"A": ("p", "q"), "B": ("p1", "q1")}.items():
    n, e, d = (int(keys[who][f], 16) for f in "ned")
    phi = (values[p] - 1) * (values[q] - 1)
    check(f"{who}: n, e, d узгоджені", n == values[p] * values[q] and e == 65537 and e * d % phi == 1)
    item = json.loads((RESULTS / "messages.json").read_text("utf-8"))[who]
    M, C, S = (int(item[f], 16) for f in "MCS")
    check(f"{who}: C = M^e, S = M^d (перерахунок через pow)", C == pow(M, e, n) and S == pow(M, d, n))
    check(f"{who}: Decrypt(C) = M, Verify(M, S)", Decrypt(C, d, n) == M and Verify(M, S, e, n))

proto = json.loads((RESULTS / "protocol.json").read_text("utf-8"))
na, ea, da = (int(keys["A"][f], 16) for f in "ned")
nb, eb, db = (int(keys["B"][f], 16) for f in "ned")
k, S, k1, S1 = (int(proto[f], 16) for f in ("k", "S", "k1", "S1"))
check("протокол: перерахунок через pow",
      S == pow(k, da, na) and k1 == pow(k, eb, nb) and S1 == pow(S, eb, nb) and pow(S, ea, na) == k)
check("протокол: ReceiveKey приймає й повертає k", ReceiveKey(k1, S1, db, nb, ea, na) == (k, True))
check("протокол: негативні сценарії", not any(list(proto["negative"].values())[:3]) and list(proto["negative"].values())[3])

pub, priv = GenerateKeyPair(61, 53, 17)
check("приклад n=3233: d=2753", pub.n == 3233 and priv.d == 2753)
check("приклад n=3233: шифрування/підпис",
      Encrypt(65, 17, 3233) == 2790 and Decrypt(2790, 2753, 3233) == 65 and Verify(65, Sign(65, 2753, 3233), 17, 3233))
try:
    SendKey(5, 2753, 3233, 3, 2000)
    check("SendKey відхиляє n1 < n", False)
except ValueError:
    check("SendKey відхиляє n1 < n", True)

print("\nНЕВДАЧ:", len(failures))
raise SystemExit(1 if failures else 0)
