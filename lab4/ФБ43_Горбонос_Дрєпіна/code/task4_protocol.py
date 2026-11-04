import json
import random

from rsa import RESULTS, Decrypt, Encrypt, ReceiveKey, SendKey, Sign
from task3_messages import load_keys

SEED = 20261106


def main():
    rng = random.Random(SEED)
    keys = load_keys()
    a, b = keys["A"], keys["B"]

    k = rng.randrange(1, a["n"])
    S = Sign(k, a["d"], a["n"])
    k1, S1 = SendKey(k, a["d"], a["n"], b["e"], b["n"])
    received, ok = ReceiveKey(k1, S1, b["d"], b["n"], a["e"], a["n"])

    forged_S = rng.randrange(1, a["n"])
    forged_S1 = Encrypt(forged_S, b["e"], b["n"])
    _, forged_ok = ReceiveKey(k1, forged_S1, b["d"], b["n"], a["e"], a["n"])
    _, changed_k_ok = ReceiveKey((k1 + 1) % b["n"], S1, b["d"], b["n"], a["e"], a["n"])
    wrong_sender_n = b["n"]
    _, wrong_sender_ok = ReceiveKey(k1, S1, b["d"], b["n"], b["e"], wrong_sender_n)

    try:
        SendKey(k, b["d"], b["n"], a["e"], a["n"])
        small_n_rejected = False
    except ValueError:
        small_n_rejected = True

    result = {
        "k": hex(k),
        "S": hex(S),
        "k1": hex(k1),
        "S1": hex(S1),
        "k_received": hex(received),
        "S_received": hex(Decrypt(S1, b["d"], b["n"])),
        "accepted": ok,
        "k_matches": received == k,
        "negative": {
            "випадковий підпис": forged_ok,
            "змінений k1": changed_k_ok,
            "чужий відкритий ключ відправника": wrong_sender_ok,
            "SendKey при n1 < n відхилено": small_n_rejected,
        },
    }
    (RESULTS / "protocol.json").write_text(json.dumps(result, indent=2, ensure_ascii=False), "utf-8")
    print("прийнято:", ok, "; k збігається:", received == k)
    print(result["negative"])


if __name__ == "__main__":
    main()
