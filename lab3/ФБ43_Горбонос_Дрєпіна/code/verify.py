import csv

from affine import (
    ALPHABETS, CIPHER_FILE, LANG_TOP, M, N, RESULTS, bigram_to_int, decrypt, egcd, encrypt, find_candidates, int_to_bigram,
    inverse, load_json, ngrams, read_text, save_json,
)


def load_candidates(alphabet_name):
    with open(RESULTS / "task4_candidates.csv", encoding="utf-8-sig", newline="") as f:
        return [r for r in csv.DictReader(f) if r["alphabet"] == alphabet_name]


def main():
    cipher = read_text(CIPHER_FILE)
    plain = read_text(RESULTS / "decrypted.txt")
    best = load_json("task4.json")["best"]
    a, b, alphabet = best["a"], best["b"], ALPHABETS[best["alphabet"]]

    print("Повторне шифрування дає вихідний шифртекст:", encrypt(plain, a, b, alphabet) == cipher)

    a_inv = pow(a, -1, N)
    manual = "".join(
        int_to_bigram(a_inv * (bigram_to_int(cipher[i:i + 2], alphabet) - b) % N, alphabet)
        for i in range(0, len(cipher), 2))
    print(f"a^-1 = {a_inv} (pow), збіг із розшифруванням:", manual == plain)

    print("\nЩо стоїть за топ-5 біграм шифртексту:")
    mapping = []
    top = [r["bigram"] for r in load_json("task2.json")["cipher_top"]]
    for y in top:
        x = a_inv * (bigram_to_int(y, alphabet) - b) % N
        mapping.append({"y": y, "Y": bigram_to_int(y, alphabet), "x": int_to_bigram(x, alphabet), "X": x,
                        "in_lang": int_to_bigram(x, alphabet) in LANG_TOP})
        print(f"  {y} (Y={mapping[-1]['Y']}) <- {mapping[-1]['x']} (X={x})")

    hits = []
    for i, x1 in enumerate(LANG_TOP):
        for x2 in LANG_TOP[i + 1:]:
            for y1 in top:
                for y2 in top:
                    if y1 != y2:
                        _, keys = find_candidates([y1, y2], alphabet, [x1, x2])
                        if (a, b) in keys:
                            hits.append((x1, x2, y1, y2))
    unique = sorted({h for h in hits})
    print("\nКількість систем, що дають правильний ключ:", len(unique))
    for h in unique:
        print("  ", h)

    kp1_top = load_json("task2.json")["kp1_top_disjoint"]
    _, keys = find_candidates(top, alphabet, kp1_top)
    print(f"\nЯкщо взяти топ-5 КП1 {kp1_top}: кандидатів {len(keys)}, правильний ключ серед них:", (a, b) in keys)

    bigrams = ngrams(plain, 2, 2).most_common(5)
    cross = ngrams(plain[1:], 2, 2).most_common(5)
    print("Топ-5 біграм відкритого тексту (без перетину):", bigrams)
    print("Топ-5 біграм на перетині:", cross)
    print("Довжина відкритого тексту:", len(plain), "m =", M)

    _, all_keys = find_candidates(top, alphabet)
    close = [(p, q) for p, q in all_keys if p % M == a % M and q % M == b % M and (p, q) != (a, b)]
    candidates = {(int(r["a"]), int(r["b"])): r for r in load_candidates(best["alphabet"])}
    share = []
    for p, q in close:
        dec = decrypt(cipher, p, q, alphabet)
        share.append(sum(dec[i] == plain[i] for i in range(1, len(plain), 2)) / (len(plain) // 2))
    c3_close = [float(candidates[k]["c_forbidden"]) for k in close]
    print(f"\nКандидати з тими самими a mod 31 = {a % M}, b mod 31 = {b % M}: {len(close)}")
    print(f"Збіг парних літер x2i з правильним текстом: від {min(share):.4f} до {max(share):.4f}")
    print(f"Частка заборонених біграм у них: від {min(c3_close):.4f} до {max(c3_close):.4f}")

    X1, X2 = bigram_to_int("то", alphabet), bigram_to_int("на", alphabet)
    Y1, Y2 = bigram_to_int("йа", alphabet), bigram_to_int("рщ", alphabet)
    dx, dy = (X1 - X2) % N, (Y1 - Y2) % N
    dx_inv = inverse(dx, N)
    found_a = dy * dx_inv % N
    found_b = (Y1 - found_a * X1) % N
    print(f"\nПриклад: то->йа, на->рщ: X*={X1}, X**={X2}, Y*={Y1}, Y**={Y2}")
    print(f"{dy} = a*{dx} (mod {N}), gcd={egcd(dx, N)[0]}, {dx}^-1={dx_inv}, a={found_a}, b={found_b}")

    save_json("verify.json", {
        "close_keys": {"count": len(close), "a_mod": a % M, "b_mod": b % M, "share_min": min(share), "share_max": max(share),
                       "c3_min": min(c3_close), "c3_max": max(c3_close)},
        "example": {"X1": X1, "X2": X2, "Y1": Y1, "Y2": Y2, "dx": dx, "dy": dy, "dx_inv": dx_inv, "a": found_a, "b": found_b},
        "reencrypt_ok": encrypt(plain, a, b, alphabet) == cipher,
        "a_inv": a_inv,
        "mapping": mapping,
        "systems_with_key": [list(h) for h in unique],
        "kp1_top_candidates": len(keys),
        "kp1_top_has_key": (a, b) in keys,
        "plain_top": bigrams,
        "cross_top": cross,
    })


if __name__ == "__main__":
    main()
