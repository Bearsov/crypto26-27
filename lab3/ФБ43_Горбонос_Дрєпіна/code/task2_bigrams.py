from affine import CIPHER_FILE, KP1_TEXT, LANG_TOP, ngrams, read_text, save_csv, save_json


def main():
    text = read_text(CIPHER_FILE)
    counts = ngrams(text, 2, 2)
    total = sum(counts.values())
    top = counts.most_common(5)
    print(f"Шифртекст: {len(text)} літер, {total} біграм без перетину")
    print("Топ-5 біграм шифртексту:")
    for bigram, count in top:
        print(f"  {bigram}  {count:4}  {count / total:.4f}")
    save_csv("task2_cipher_top.csv", ["bigram", "count", "frequency"],
             [[b, c, f"{c / total:.6f}"] for b, c in counts.most_common(30)])

    corpus = read_text(KP1_TEXT)
    disjoint = ngrams(corpus, 2, 2)
    overlap = ngrams(corpus, 2, 1)
    rank_d = {b: i + 1 for i, (b, _) in enumerate(disjoint.most_common())}
    rank_o = {b: i + 1 for i, (b, _) in enumerate(overlap.most_common())}
    n_d, n_o = sum(disjoint.values()), sum(overlap.values())

    print(f"\nПеревірка мови на тексті КП1 ({len(corpus)} літер)")
    print("Біграма  ранг(без перетину)  частота  ранг(з перетином)  частота")
    rows = []
    for b in LANG_TOP:
        rows.append([b, rank_d[b], f"{disjoint[b] / n_d:.6f}", rank_o[b], f"{overlap[b] / n_o:.6f}"])
        print(f"  {b}      {rank_d[b]:4}            {disjoint[b] / n_d:.4f}      {rank_o[b]:4}          {overlap[b] / n_o:.4f}")
    save_csv("task2_language_check.csv", ["bigram", "rank_disjoint", "freq_disjoint", "rank_overlap", "freq_overlap"], rows)

    kp1_top = [b for b, _ in disjoint.most_common(5)]
    print("Топ-5 КП1 без перетину:", kp1_top)
    print("Топ-5 КП1 з перетином:", [b for b, _ in overlap.most_common(5)])
    save_json("task2.json", {
        "cipher_letters": len(text),
        "cipher_bigrams": total,
        "cipher_top": [{"bigram": b, "count": c, "freq": c / total} for b, c in top],
        "kp1_letters": len(corpus),
        "kp1_top_disjoint": kp1_top,
        "kp1_top_overlap": [b for b, _ in overlap.most_common(5)],
    })


if __name__ == "__main__":
    main()
