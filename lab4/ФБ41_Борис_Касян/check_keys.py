
import json

with open("rsa_keys.json", "r", encoding="utf-8") as f:
    keys = json.load(f)

with open("rsa_task4_results.json", "r", encoding="utf-8") as f:
    results = json.load(f)

for name in ["A", "B"]:
    n = keys[name]["public"]["n"]
    e = keys[name]["public"]["e"]
    d = keys[name]["private"]["d"]

    M = results[name]["message"]
    C = results[name]["ciphertext"]
    S = results[name]["signature"]

    print("\nАбонент", name)
    print("Модуль n =", n)
    print("0 <= M < n:", 0 <= M < n)
    print("C = M^e mod n:", pow(M, e, n) == C)
    print("M = C^d mod n:", pow(C, d, n) == M)
    print("S = M^d mod n:", pow(M, d, n) == S)
    print("M = S^e mod n:", pow(S, e, n) == M)
