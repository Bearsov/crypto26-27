from affine import ALPHABETS, LANG_TOP, find_candidates, load_json, save_csv, save_json


def main():
    data = load_json("task2.json")
    cipher_top = [row["bigram"] for row in data["cipher_top"]]
    print("Мова:", LANG_TOP)
    print("Шифртекст:", cipher_top)
    summary = {}
    for name, alphabet in ALPHABETS.items():
        systems, keys = find_candidates(cipher_top, alphabet)
        stats = {
            "systems": len(systems),
            "d1": sum(s["d"] == 1 for s in systems),
            "d_gt1": sum(s["d"] > 1 for s in systems),
            "no_roots": sum(s["roots"] == 0 for s in systems),
            "multi_roots": sum(s["roots"] > 1 for s in systems),
            "total_roots": sum(s["roots"] for s in systems),
            "invalid_a": sum(s["roots"] - s["valid"] for s in systems),
            "unique_keys": len(keys),
        }
        summary[name] = {"stats": stats, "keys": keys}
        print(f"\nАлфавіт {name}: {alphabet}")
        for key, value in stats.items():
            print(f"  {key:12} {value}")
        save_csv(f"task3_systems_{name}.csv", ["x1", "x2", "y1", "y2", "d", "roots", "valid"],
                 [[s[k] for k in ("x1", "x2", "y1", "y2", "d", "roots", "valid")] for s in systems])
    save_json("task3.json", summary)


if __name__ == "__main__":
    main()
