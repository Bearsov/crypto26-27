import json
import random
import sys

from rsa import DATA, RESULTS, Decrypt, Encrypt, ReceiveKey, SendKey, Sign, Verify
from task3_messages import load_keys

SEED = 20261107
SESSION = DATA / "server_session.json"


def to_hex(value):
    text = f"{value:X}"
    return text if len(text) % 2 == 0 else "0" + text


def number(text):
    return int(text, 16)


def prepare(n_512, e_512, n_1024, e_1024):
    rng = random.Random(SEED)
    a = load_keys()["A"]
    limit = min(a["n"], n_512)
    M1, M2, M3, M4 = (rng.randrange(1, limit) for _ in range(4))
    k = rng.randrange(1, a["n"])
    k1, S1 = SendKey(k, a["d"], a["n"], e_1024, n_1024)
    return {
        "n_A": to_hex(a["n"]), "e_A": to_hex(a["e"]),
        "encrypt_local": {"M": to_hex(M1), "C": to_hex(Encrypt(M1, e_512, n_512))},
        "encrypt_on_server_M": to_hex(M2),
        "sign_on_server_M": to_hex(M3),
        "sign_local": {"M": to_hex(M4), "S": to_hex(Sign(M4, a["d"], a["n"]))},
        "send_local": {"k": to_hex(k), "k1": to_hex(k1), "S1": to_hex(S1)},
    }


def check():
    s = json.loads(SESSION.read_text("utf-8"))
    a = load_keys()["A"]
    n512, e512 = number(s["server_512"]["modulus"]), number(s["server_512"]["publicExponent"])
    n256, e256 = number(s["server_256"]["modulus"]), number(s["server_256"]["publicExponent"])
    n1024, e1024 = number(s["server_1024"]["modulus"]), number(s["server_1024"]["publicExponent"])
    enc, dec, sig, ver, snd, rcv = (s[f] for f in
                                    ("encrypt_local", "encrypt_server", "sign_server", "verify_server", "send_server", "receive_server"))
    k_got, k_ok = ReceiveKey(number(snd["key"]), number(snd["signature"]), a["d"], a["n"], e256, n256)
    extra = s["send_server_512"]
    k_512, ok_512 = ReceiveKey(number(extra["key"]), number(extra["signature"]), a["d"], a["n"], e512, n512)
    S_512 = Decrypt(number(extra["signature"]), a["d"], a["n"])
    result = {
        "Encrypt локально -> Decrypt на сервері": Encrypt(number(enc["M"]), e512, n512) == number(enc["C"])
                                                  and number(enc["server_message"]) == number(enc["M"]),
        "Encrypt на сервері -> Decrypt локально": Decrypt(number(dec["cipherText"]), a["d"], a["n"]) == number(dec["M"]),
        "Sign на сервері -> Verify локально": Verify(number(sig["M"]), number(sig["signature"]), e512, n512),
        "Sign локально -> Verify на сервері": Sign(number(ver["M"]), a["d"], a["n"]) == number(ver["S"]) and ver["verified"] is True,
        "SendKey на сервері -> ReceiveKey локально": k_ok,
        "SendKey локально -> ReceiveKey на сервері": SendKey(number(rcv["k"]), a["d"], a["n"], e1024, n1024) == (number(rcv["k1"]), number(rcv["S1"]))
                                                     and number(rcv["key"]) == number(rcv["k"]) and rcv["verified"] is True,
        "Локальний Verify відхиляє підпис зі зміненим останнім бітом": not Verify(number(ver["M"]), number(ver["S_changed"]), a["e"], a["n"]),
    }
    result["k від сервера (ключ 256 біт): біт"] = k_got.bit_length()
    result["спроба при n_сервера > n_A: прийнято"] = ok_512
    result["спроба при n_сервера > n_A: S підпису < n_A"] = S_512 < a["n"]
    result["k, отриманий від сервера"] = hex(k_got)
    result["k від сервера при n_сервера > n_A"] = hex(k_512)
    (RESULTS / "server_check.json").write_text(json.dumps(result, indent=2, ensure_ascii=False), "utf-8")
    for name, value in result.items():
        print(f"{name}: {value}")
    return all(v for name, v in result.items() if isinstance(v, bool) and not name.startswith("спроба"))


if __name__ == "__main__":
    if sys.argv[1:2] == ["prepare"]:
        args = [int(x, 16) for x in sys.argv[2:6]]
        print(json.dumps(prepare(*args), indent=1))
    else:
        raise SystemExit(0 if check() else 1)
