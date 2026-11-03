from collections import Counter
from statistics import mean, pstdev
from affine import FOLDER, decrypt, normalize, read_ciphertext


FREQUENT_BIGRAMS = ("ст", "но", "то", "на", "ен")


def bigram_frequencies(text):
    positions = range(1, len(text) - 1, 2)
    total = len(positions)
    if total == 0:
        raise ValueError("Текст надто короткий для аналізу біграм на межах пар")
    counts = Counter(text[i:i + 2] for i in positions)
    return {bigram: counts[bigram] / total for bigram in FREQUENT_BIGRAMS}


def calculate_thresholds(reference, fragment_length):
    fragments = [reference[i:i + fragment_length]
                 for i in range(0, len(reference) - fragment_length + 1, fragment_length)]
    if len(fragments) < 2:
        raise ValueError("Мовний еталон має містити щонайменше два повні фрагменти")

    reference_frequencies = [bigram_frequencies(fragment) for fragment in fragments]
    statistics = {}
    for bigram in FREQUENT_BIGRAMS:
        values = [freqs[bigram] for freqs in reference_frequencies]
        average = mean(values)
        deviation = pstdev(values)
        statistics[bigram] = (average, deviation, max(0.0, average - 3 * deviation))
    return len(fragments), statistics


if __name__ == "__main__":
    ciphertext = read_ciphertext()
    reference = normalize((FOLDER / "output_without_spaces.txt").read_text(encoding="utf-8"))
    fragment_count, statistics = calculate_thresholds(reference, len(ciphertext))
    thresholds = {bigram: statistics[bigram][2] for bigram in FREQUENT_BIGRAMS}

    keys = [tuple(map(int, line.split()))
            for line in (FOLDER / "keys.txt").read_text(encoding="utf-8").splitlines()
            if line.strip()]
    if not keys:
        raise ValueError("У keys.txt немає кандидатів. Запустіть 2.keys.py")

    results = []
    for a, b in keys:
        plaintext = decrypt(ciphertext, a, b)
        frequencies = bigram_frequencies(plaintext)
        total_frequency = sum(frequencies.values())
        accepted = all(frequencies[bigram] >= thresholds[bigram]
                       for bigram in FREQUENT_BIGRAMS)
        results.append((total_frequency, a, b, accepted, frequencies, plaintext))
    results.sort(key=lambda row: (-row[0], row[1], row[2]))
    accepted_keys = [row for row in results if row[3]]

    print("Критерій частих біграм (№2 із методички)")
    print("Біграми перевіряються на межах розшифрованих пар")
    print("Еталонних фрагментів:", fragment_count)
    print("Біграма   Середня частота   Ст. відхилення   Мін. частота")
    for bigram in FREQUENT_BIGRAMS:
        average, deviation, threshold = statistics[bigram]
        print(f"{bigram:>6}      {average:.6f}          {deviation:.6f}        {threshold:.6f}")
    print(" a    b    Сума частот   Прийнято")
    for total_frequency, a, b, accepted, frequencies, plaintext in results[:5]:
        print(f"{a:>3}  {b:>3}     {total_frequency:.6f}      {'так' if accepted else 'ні'}")
    print("Кандидатів, що пройшли критерій:", len(accepted_keys))

    header = "a b total_frequency " + " ".join(FREQUENT_BIGRAMS) + " accepted\n"
    table = header + "".join(
        f"{a} {b} {total_frequency:.9f} "
        + " ".join(f"{frequencies[bigram]:.9f}" for bigram in FREQUENT_BIGRAMS)
        + f" {int(accepted)}\n"
        for total_frequency, a, b, accepted, frequencies, plaintext in results
    )
    (FOLDER / "scores.txt").write_text(table, encoding="utf-8")

    if len(accepted_keys) != 1:
        raise ValueError("Критерій не дав єдиного ключа: перевірте scores.txt і мовний еталон")

    total_frequency, a, b, accepted, frequencies, plaintext = accepted_keys[0]
    (FOLDER / "key.txt").write_text(f"{a} {b}\n", encoding="utf-8")
    (FOLDER / "decrypted.txt").write_text(plaintext + "\n", encoding="utf-8")
    print(f"Знайдений ключ: a = {a}, b = {b}")
    print("Частоти біграм правильного тексту:")
    for bigram in FREQUENT_BIGRAMS:
        print(f"  {bigram}: {frequencies[bigram]:.6f} (поріг {thresholds[bigram]:.6f})")
    print("Розшифровано літер:", len(plaintext))
    print("Початок тексту:")
    print(plaintext[:90])
    print(plaintext[90:180])
    print("Повний текст збережено в decrypted.txt")
