import json

from rsa import RESULTS, GenerateKeyPair, gcd, mod_pow


def load_primes():
    data = json.loads((RESULTS / "primes.json").read_text("utf-8"))["primes"]
    return {name: int(item["p"], 16) for name, item in data.items()}


def key_json(pub, priv):
    return {
        "n": hex(pub.n), "e": hex(pub.e), "d": hex(priv.d), "p": hex(priv.p), "q": hex(priv.q),
        "n_bits": pub.n.bit_length(), "phi": hex((priv.p - 1) * (priv.q - 1)),
    }


def checks(pub, priv):
    phi = (priv.p - 1) * (priv.q - 1)
    probe = 0x1234567890ABCDEF
    return {
        "n = p*q": pub.n == priv.p * priv.q,
        "phi(n) = (p-1)(q-1)": phi == (priv.p - 1) * (priv.q - 1),
        "p != q": priv.p != priv.q,
        "2 <= e <= phi-1": 2 <= pub.e <= phi - 1,
        "gcd(e, phi) = 1": gcd(pub.e, phi) == 1,
        "e*d mod phi = 1": pub.e * priv.d % phi == 1,
        "0 < d < phi": 0 < priv.d < phi,
        "(M^e)^d mod n = M": mod_pow(mod_pow(probe, pub.e, pub.n), priv.d, pub.n) == probe,
    }


def main():
    primes = load_primes()
    pub_a, priv_a = GenerateKeyPair(primes["p"], primes["q"])
    pub_b, priv_b = GenerateKeyPair(primes["p1"], primes["q1"])
    result = {
        "A": key_json(pub_a, priv_a),
        "B": key_json(pub_b, priv_b),
        "checks_A": checks(pub_a, priv_a),
        "checks_B": checks(pub_b, priv_b),
        "n_A <= n_B": pub_a.n <= pub_b.n,
    }
    (RESULTS / "keys.json").write_text(json.dumps(result, indent=2, ensure_ascii=False), "utf-8")
    print("n_A =", hex(pub_a.n), pub_a.n.bit_length(), "біт")
    print("n_B =", hex(pub_b.n), pub_b.n.bit_length(), "біт")
    print("n_A <= n_B:", result["n_A <= n_B"])
    for name, ok in result["checks_A"].items():
        print(f"A: {name}: {ok}")
    print("Усі перевірки B:", all(result["checks_B"].values()))


if __name__ == "__main__":
    main()
