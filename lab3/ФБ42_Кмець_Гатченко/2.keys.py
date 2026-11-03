from itertools import permutations
from math import gcd
from affine import FOLDER, MODULUS, bigram_number, solve_congruence

LANGUAGE_BIGRAMS = ["ст", "но", "то", "на", "ен"]


if __name__ == "__main__":
    top = (FOLDER / "top_bigrams.txt").read_text(encoding="utf-8").split()
    if len(top) != 5 or len(set(top)) != 5:
        raise ValueError("Спочатку запустіть 1.frequency.py")
    keys = set()
    total = 0
    no_solutions = 0
    multiple = 0
    invalid = 0
    for x1, x2 in permutations(LANGUAGE_BIGRAMS, 2):
        for y1, y2 in permutations(top, 2):
            total += 1
            dx = bigram_number(x1) - bigram_number(x2)
            dy = bigram_number(y1) - bigram_number(y2)
            solutions = solve_congruence(dx, dy, MODULUS)
            if not solutions:
                no_solutions += 1
            if len(solutions) > 1:
                multiple += 1
            for a in solutions:
                if gcd(a, MODULUS) != 1:
                    invalid += 1
                    continue
                b = (bigram_number(y1) - a * bigram_number(x1)) % MODULUS
                keys.add((a, b))

    print("Перевірено зіставлень:", total)
    print("Порівнянь без розв'язків:", no_solutions)
    print("Порівнянь із кількома розв'язками:", multiple)
    print("Відкинуто необоротних значень a:", invalid)
    print("Унікальних кандидатів (a, b):", len(keys))
    print("Перші 8 кандидатів:", sorted(keys)[:8])
    result = "".join(f"{a} {b}\n" for a, b in sorted(keys))
    (FOLDER / "keys.txt").write_text(result, encoding="utf-8")
    print("Кандидатів збережено в keys.txt")
