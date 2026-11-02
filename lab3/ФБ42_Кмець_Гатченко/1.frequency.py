from collections import Counter
from affine import FOLDER, normalize, read_ciphertext


if __name__ == "__main__":
    text = read_ciphertext()
    reference = normalize((FOLDER / "output_without_spaces.txt").read_text(encoding="utf-8"))
    counts = Counter(text[i:i + 2] for i in range(0, len(text), 2))
    reference_counts = Counter(reference[i:i + 2] for i in range(0, len(reference) - 1, 2))

    print(f"Варіант 5: {len(text)} літер, {len(text) // 2} біграм")
    print("П'ять найчастіших біграм шифртексту:")
    print("Біграма  Кількість  Частота")
    for bigram, count in counts.most_common(5):
        print(f"   {bigram}      {count:>3}      {count / (len(text) // 2):.6f}")

    print(f"\nТекст з КП1: {len(reference)} літер")
    print("П'ять найчастіших біграм тексту з КП1:")
    for bigram, count in reference_counts.most_common(5):
        print(f"   {bigram}     {count:>4}      {count / (len(reference) // 2):.6f}")
    print("Типові біграми з методички: ст, но, то, на, ен")
    print("Їхні ранги в тексті з КП1:")
    ordered = [bigram for bigram, count in reference_counts.most_common()]
    for bigram in ["ст", "но", "то", "на", "ен"]:
        print(f"   {bigram}: {ordered.index(bigram) + 1}")

    top = [bigram for bigram, count in counts.most_common(5)]
    (FOLDER / "top_bigrams.txt").write_text("\n".join(top) + "\n", encoding="utf-8")
