import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from affine import (
    ALPHABETS, ARTIFACTS, CIPHER_FILE, DATA, KP1_TEXT, RESULTS, T_FORBIDDEN, T_FREQUENT, T_RARE,
    decrypt, find_candidates, is_russian, load_forbidden, load_json, measure, ngrams, read_text,
    save_csv, save_json,
)

FRAGMENT = 2500


def calibrate(forbidden):
    corpus = read_text(KP1_TEXT)
    half = len(corpus) // 2
    parts = [corpus[i:i + FRAGMENT] for i in range(half, len(corpus) - FRAGMENT, FRAGMENT)]
    values = [measure(p, forbidden) for p in parts]
    c1, c2, c3 = zip(*values)
    result = {
        "fragments": len(parts), "length": FRAGMENT,
        "c1_min": min(c1), "c1_mean": sum(c1) / len(c1), "c1_max": max(c1),
        "c2_min": min(c2), "c2_mean": sum(c2) / len(c2), "c2_max": max(c2),
        "c3_min": min(c3), "c3_mean": sum(c3) / len(c3), "c3_max": max(c3),
    }
    print(f"Калібрування на {len(parts)} фрагментах КП1 по {FRAGMENT} літер (друга половина тексту)")
    print(f"  частка о,а,е: {result['c1_min']:.4f} .. {result['c1_max']:.4f}, поріг >= {T_FREQUENT}")
    print(f"  частка ф,щ,ь: {result['c2_min']:.4f} .. {result['c2_max']:.4f}, поріг <= {T_RARE}")
    print(f"  заборонені на перетині: {result['c3_min']:.4f} .. {result['c3_max']:.4f}, поріг <= {T_FORBIDDEN}")
    return result


def attack(text, forbidden):
    top = [b for b, _ in ngrams(text, 2, 2).most_common(5)]
    rows = []
    for name, alphabet in ALPHABETS.items():
        _, keys = find_candidates(top, alphabet)
        for a, b in keys:
            plain = decrypt(text, a, b, alphabet)
            c1, c2, c3 = measure(plain, forbidden)
            rows.append({
                "alphabet": name, "a": a, "b": b, "c1": c1, "c2": c2, "c3": c3,
                "passed": is_russian(plain, forbidden), "start": plain[:40],
            })
    return top, rows


def test_set(forbidden):
    print("\nПеревірка на for_test")
    print("файл  літер кандидатів пройшли  алфавіт     a     b   о,а,е   ф,щ,ь  заборон.  початок тексту")
    table = []
    for i in range(1, 16):
        text = read_text(DATA / "for_test" / f"V{i}.txt")
        _, rows = attack(text, forbidden)
        passed = [r for r in rows if r["passed"]]
        for r in passed or [None]:
            line = [f"V{i}", len(text), len(rows), len(passed)]
            line += [r["alphabet"], r["a"], r["b"], f"{r['c1']:.4f}", f"{r['c2']:.4f}", f"{r['c3']:.5f}", r["start"][:30]] if r else ["-"] * 7
            table.append(line)
            print("{:5} {:5} {:7} {:6}   {:6} {:5} {:5} {:7} {:7} {:8}  {}".format(*line))
    save_csv("task4_for_test.csv", ["file", "letters", "candidates", "passed", "alphabet", "a", "b", "c_frequent", "c_rare", "c_forbidden", "start"], table)
    return table


def plot(rows, path):
    ARTIFACTS.mkdir(exist_ok=True)
    fig, ax = plt.subplots(figsize=(7.5, 4.6), dpi=170)
    wrong = [r for r in rows if not r["passed"] and not (r["a"] == 27 and r["b"] == 211)]
    near = [r for r in rows if not r["passed"] and r["a"] == 27 and r["b"] == 211]
    good = [r for r in rows if r["passed"]]
    ax.scatter([r["c3"] for r in wrong], [r["c1"] for r in wrong], s=18, color="#9aa3ad", label="неправильний ключ")
    ax.scatter([r["c3"] for r in near], [r["c1"] for r in near], s=70, marker="s", color="#d9822b",
               label="ключ (27, 211), порядок ы, ь")
    ax.scatter([r["c3"] for r in good], [r["c1"] for r in good], s=90, marker="*", color="#1f6fb2",
               label="ключ (27, 211), порядок ь, ы")
    ax.axhline(T_FREQUENT, color="#555555", lw=1, ls="--")
    ax.axvline(T_FORBIDDEN, color="#555555", lw=1, ls=":")
    ax.text(0.198, T_FREQUENT + 0.003, "поріг о,а,е = 0,24", fontsize=8, color="#333333", ha="right")
    ax.text(T_FORBIDDEN + 0.0015, 0.075, "поріг заборонених = 0,001", fontsize=8, color="#333333", rotation=90)
    ax.set_xlabel("Частка заборонених біграм на перетині")
    ax.set_ylabel("Частка літер о, а, е")
    ax.grid(alpha=0.25)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(frameon=False, fontsize=8, loc="upper right", bbox_to_anchor=(1, 0.86))
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def main():
    forbidden = load_forbidden()
    print(f"Заборонених біграм (0 разів у першій половині тексту КП1): {len(forbidden)}")
    calibration = calibrate(forbidden)
    table = test_set(forbidden)

    text = read_text(CIPHER_FILE)
    top, rows = attack(text, forbidden)
    rows.sort(key=lambda r: r["c3"])
    print("\nВаріант 2: найкращі кандидати за критерієм заборонених біграм")
    print("алфавіт    a    b   о,а,е   ф,щ,ь  заборон.  рішення  початок")
    for r in rows[:6]:
        verdict = "прийнято" if r["passed"] else "відкинуто"
        print(f"{r['alphabet']:6} {r['a']:4} {r['b']:4}  {r['c1']:.4f}  {r['c2']:.4f}  {r['c3']:.4f}   {verdict:9} {r['start'][:28]}")
    passed = [r for r in rows if r["passed"]]
    print(f"Усього кандидатів: {len(rows)}, пройшло: {len(passed)}")
    assert len(passed) == 1

    best = passed[0]
    plain = decrypt(text, best["a"], best["b"], ALPHABETS[best["alphabet"]])
    RESULTS.mkdir(exist_ok=True)
    (RESULTS / "decrypted.txt").write_text(plain, encoding="utf-8")
    (RESULTS / "key.txt").write_text(
        f"a = {best['a']}\nb = {best['b']}\nалфавіт = {ALPHABETS[best['alphabet']]}\n", encoding="utf-8")
    save_csv("task4_candidates.csv", ["alphabet", "a", "b", "c_frequent", "c_rare", "c_forbidden", "passed", "start"],
             [[r["alphabet"], r["a"], r["b"], f"{r['c1']:.6f}", f"{r['c2']:.6f}", f"{r['c3']:.6f}", r["passed"], r["start"]] for r in rows])
    plot(rows, ARTIFACTS / "task4_recognizer.png")

    wrong_rows = [r for r in rows if not r["passed"] and not (r["a"] == best["a"] and r["b"] == best["b"])]
    save_json("task4.json", {
        "forbidden_count": len(forbidden),
        "forbidden": sorted(forbidden),
        "calibration": calibration,
        "candidates": len(rows),
        "best": best,
        "other_alphabet": next(r for r in rows if r["a"] == best["a"] and r["b"] == best["b"] and not r["passed"]),
        "wrong_stats": {
            "count": len(wrong_rows),
            "c1_max": max(r["c1"] for r in wrong_rows),
            "c2_min": min(r["c2"] for r in wrong_rows),
            "c3_min": min(r["c3"] for r in wrong_rows),
            "pass_c1": sum(r["c1"] >= T_FREQUENT for r in wrong_rows),
            "pass_c2": sum(r["c2"] <= T_RARE for r in wrong_rows),
            "pass_c3": sum(r["c3"] <= T_FORBIDDEN for r in wrong_rows),
        },
        "for_test": table,
    })
    print(f"\nКлюч: a = {best['a']}, b = {best['b']}, алфавіт {best['alphabet']}")
    print("Початок тексту:", plain[:120])


if __name__ == "__main__":
    main()
