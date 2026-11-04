import json
import random

from rsa import RESULTS, Decrypt, Encrypt, Sign, Verify

SEED = 20261105


def load_keys():
    data = json.loads((RESULTS / "keys.json").read_text("utf-8"))
    return {who: {f: int(data[who][f], 16) for f in ("n", "e", "d")} for who in ("A", "B")}


def run(owner, rng):
    n, e, d = owner["n"], owner["e"], owner["d"]
    M = rng.randrange(1, n)
    C = Encrypt(M, e, n)
    S = Sign(M, d, n)
    return {
        "M": hex(M), "C": hex(C), "decrypted": hex(Decrypt(C, d, n)),
        "decrypt_ok": Decrypt(C, d, n) == M,
        "S": hex(S),
        "verify_ok": Verify(M, S, e, n),
        "verify_changed_message": Verify((M + 1) % n, S, e, n),
        "verify_changed_signature": Verify(M, (S + 1) % n, e, n),
    }


def main():
    rng = random.Random(SEED)
    keys = load_keys()
    result = {who: run(keys[who], rng) for who in ("A", "B")}
    (RESULTS / "messages.json").write_text(json.dumps(result, indent=2, ensure_ascii=False), "utf-8")
    for who, item in result.items():
        print(who, {k: v for k, v in item.items() if isinstance(v, bool)})


if __name__ == "__main__":
    main()
