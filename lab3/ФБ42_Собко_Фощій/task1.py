from common import M, M2, egcd, inverse, solve_congruence

print(f'm = {M}, m² = {M2}')

print('\nРозширений алгоритм Евкліда:')
for a, b in ((240, 46), (200, 961), (31, 961)):
    d, x, y = egcd(a, b)
    print(f'egcd({a}, {b}) = ({d}, {x}, {y}); перевірка: {a*x+b*y}')
    assert a*x + b*y == d

print('\nОбернений елемент:')
for a in (200, 441, 711, 31, 62):
    inv = inverse(a, M2)
    print(f'{a}⁻¹ mod {M2} = {inv}')
    assert inv is None or a * inv % M2 == 1

print('\nЛінійні порівняння:')
for a, b, n in ((6, 12, 18), (2, 3, 4), (200, 1, M2), (31, 62, M2)):
    roots = solve_congruence(a, b, n)
    print(f'{a}x ≡ {b} (mod {n}): {len(roots)} розв’язків, {roots[:8]}')
    assert all((a*x-b) % n == 0 for x in roots)
