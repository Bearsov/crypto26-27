import json
import random

from rsa import RESULTS, random_prime_bits

SEED = 20261104
BITS = 256


def describe(search):
    return {
        "p": hex(search.p),
        "bits": search.p.bit_length(),
        "x": hex(search.x),
        "m0": hex(search.m0),
        "tested": len(search.rejected_trial) + len(search.rejected_mr) + 1,
        "rejected_trial": [
            {"i": i, "candidate": hex(c), "divisor": m} for i, c, m in search.rejected_trial
        ],
        "rejected_mr": [
            {"i": i, "candidate": hex(c), "witness": hex(w)} for i, c, w, _ in search.rejected_mr
        ],
        "mr_rounds_passed": len(search.traces),
    }


def trace_json(trace):
    return {
        "x": hex(trace["x"]),
        "d": hex(trace["d"]),
        "s": trace["s"],
        "passed": trace["passed"],
        "steps": [{"name": n, "r": r, "value": hex(v)} for n, r, v in trace["steps"]],
    }


def main():
    RESULTS.mkdir(exist_ok=True)
    random.seed(SEED)
    pairs = [[random_prime_bits(BITS) for _ in range(2)] for _ in range(2)]
    swapped = pairs[0][0].p * pairs[0][1].p > pairs[1][0].p * pairs[1][1].p
    if swapped:
        pairs.reverse()
    named = dict(zip(("p", "q", "p1", "q1"), (s for pair in pairs for s in pair)))

    best = max(named, key=lambda name: named[name].traces[0]["s"])
    shown = max(enumerate(named[best].traces), key=lambda item: len(item[1]["steps"]))
    rejected = next(s for s in named.values() if s.rejected_mr).rejected_mr[0]
    result = {
        "seed": SEED,
        "bits": BITS,
        "swapped_pairs": swapped,
        "primes": {name: describe(s) for name, s in named.items()},
        "mr_trace": {
            "prime_name": best,
            "prime": hex(named[best].p),
            "round": shown[0] + 1,
            "trace": trace_json(shown[1]),
        },
        "mr_rejected_trace": {
            "candidate": hex(rejected[1]),
            "trace": trace_json(rejected[3]),
        },
    }
    (RESULTS / "primes.json").write_text(json.dumps(result, indent=2, ensure_ascii=False), "utf-8")

    for name, s in named.items():
        print(f"{name} = {hex(s.p)} ({s.p.bit_length()} біт); перевірено {len(s.rejected_trial) + len(s.rejected_mr) + 1}, "
              f"відкинуто діленням {len(s.rejected_trial)}, Міллером-Рабіном {len(s.rejected_mr)}")
    print("pq <= p1q1:", named["p"].p * named["q"].p <= named["p1"].p * named["q1"].p, "; пари поміняно:", swapped)
    print("Трасування Міллера-Рабіна для", best, "s =", named[best].traces[0]["s"])


if __name__ == "__main__":
    main()
