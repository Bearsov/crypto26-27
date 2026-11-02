import random

from affine import N, egcd, inverse, save_csv, solve_congruence


def main():
    print("Розширений алгоритм Евкліда: d = u*a + v*b")
    rows = []
    for a, b in [(240, 46), (27, 961), (31, 961), (17, 3120)]:
        d, u, v = egcd(a, b)
        assert d == u * a + v * b
        rows.append([a, b, d, u, v])
        print(f"a={a:5} b={b:5} d={d:3} u={u:5} v={v:5}")
    save_csv("task1_egcd.csv", ["a", "b", "d", "u", "v"], rows)

    print("\nОбернений елемент за модулем 961")
    rows = []
    for a in [27, 2, 30, 960]:
        inv = inverse(a, N)
        assert a * inv % N == 1
        rows.append([a, inv, a * inv % N])
        print(f"{a}^-1 = {inv}, перевірка: {a}*{inv} mod 961 = {a * inv % N}")
    save_csv("task1_inverse.csv", ["a", "a_inv", "check"], rows)

    print("\nЛінійні порівняння ax = b (mod n)")
    rows = []
    for a, b, n, case in [
        (27, 400, 961, "1) d = 1"),
        (62, 100, 961, "2.1) d = 31, b не ділиться на d"),
        (62, 124, 961, "2.2) d = 31, b ділиться на d"),
        (6, 4, 8, "2.2) d = 2"),
    ]:
        roots = solve_congruence(a, b, n)
        assert all(a * x % n == b % n for x in roots)
        shown = roots if len(roots) <= 4 else roots[:3] + ["...", roots[-1]]
        rows.append([a, b, n, case, len(roots), " ".join(map(str, roots))])
        print(f"{a}x = {b} (mod {n}) [{case}]: розв'язків {len(roots)}: {shown}")
    save_csv("task1_congruences.csv", ["a", "b", "n", "case", "count", "roots"], rows)

    random.seed(3)
    checks = 0
    for _ in range(100000):
        n = random.choice([961, 31, 8, 100, 1024])
        a, b = random.randrange(n), random.randrange(n)
        roots = solve_congruence(a, b, n)
        assert sorted(roots) == [x for x in range(n) if a * x % n == b]
        checks += 1
    print(f"\nПеревірка повним перебором: {checks} випадкових порівнянь, розбіжностей 0")


if __name__ == "__main__":
    main()
