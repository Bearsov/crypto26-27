import os
from collections import Counter
from math import gcd

from tabulate import tabulate

from src.vigenere import M, CHAR_TO_IDX, IDX_TO_CHAR, clean_text, encrypt, decrypt
from src.stats import calc_ic, calc_dr, get_blocks, avg_ic_for_r
from src.attack import RUS_FREQS, recover_key_chisquare

MAX_R = 30
I_LANG = sum(p * p for p in RUS_FREQS.values())  # теоретичний I мови
I_RANDOM = 1 / M                                  # I рівноімовірного алфавіту


def read_clean(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return clean_text(f.read())


# ---------------------------------------------------------------------------
# 0. Дані
# ---------------------------------------------------------------------------
os.makedirs("data", exist_ok=True)
ciphertext = read_clean("data/ciphertext_v10.txt")
n = len(ciphertext)

print(f"=== Шифртекст варіанта 10: {n} символів ===")
print(f"I(ШТ) = {calc_ic(ciphertext):.5f}   "
      f"I мови = {I_LANG:.5f}   I0 = 1/{M} = {I_RANDOM:.5f}")

# ---------------------------------------------------------------------------
# 1. Дослідження шифру на власному тексті
# ---------------------------------------------------------------------------
sample_path = "data/sample_text.txt"
if os.path.exists(sample_path) and os.path.getsize(sample_path) > 0:
    sample_pt = read_clean(sample_path)
    print(f"\n--- Завдання 1. Власний ВТ: {len(sample_pt)} літер ---")
    if len(sample_pt) < 2000:
        print("УВАГА: за завданням потрібно 2-3 КБ тексту; "
              "візьміть довший відкритий текст.")

    test_keys = ["да", "мир", "ключ", "слово", "шелестстраниц"]  # r = 2,3,4,5,13
    rows = [["Відкритий текст", "-", "-", f"{calc_ic(sample_pt):.5f}"]]
    for k in test_keys:
        rows.append([f"Шифртекст", k, len(k),
                     f"{calc_ic(encrypt(sample_pt, k)):.5f}"])
    print(tabulate(rows, headers=["Текст", "Ключ", "r", "I"], tablefmt="github"))

# ---------------------------------------------------------------------------
# 2. Пошук періоду r
# ---------------------------------------------------------------------------
print("\n--- Завдання 2. Пошук періоду r (r = 2..%d) ---" % MAX_R)
stats = []
for r in range(2, MAX_R + 1):
    stats.append((r, avg_ic_for_r(ciphertext, r), calc_dr(ciphertext, r)))

rows = [[r, f"{ic:.5f}", d, f"{d / (n - r):.5f}", n // r] for r, ic, d in stats]
print(tabulate(rows, headers=["r", "Avg IC", "D_r", "D_r/(n-r)", "довж. блока"],
               tablefmt="github"))

# Автоматичний вибір: найменше r, для якого середній IC ближчий до I мови,
# ніж до I0 (поріг - середина між ними). Кратні істинному періоду
# (2r, 3r, ...) теж пройдуть поріг, тому беремо найменше.
threshold = (I_LANG + I_RANDOM) / 2
candidates = [r for r, ic, _ in stats if ic > threshold]
if not candidates:
    raise SystemExit("Жоден r не перевищив поріг - перевірте шифртекст.")
best_r = min(candidates)
print(f"\nПоріг IC = {threshold:.5f}; кандидати вище порогу: {candidates}")
print(f"Найменший з них, r = {best_r}, приймаємо за період "
      f"(решта кратні {best_r}: "
      f"{all(c % best_r == 0 for c in candidates)})")

# Аналіз альтернативних кандидатів: дільники та кратні істинного r.
# Якщо r кратне d | best_r, у блоці змішано best_r/d різних зсувів Цезаря.
print("\nАльтернативні кандидати (блок змішує s різних зсувів):")
ic_by_r = {r: ic for r, ic, _ in stats}
alt_rows = []
for r in sorted(ic_by_r):
    g = gcd(r, best_r)
    s = 1 if r % best_r == 0 else best_r // g
    pred = I_LANG / s + (1 - 1 / s) * I_RANDOM
    if g > 1:  # r має спільний дільник з r* -> очікуємо проміжні значення IC
        alt_rows.append([r, f"gcd={g}", s, f"{ic_by_r[r]:.5f}", f"{pred:.5f}"])
print(tabulate(alt_rows, headers=["r", "gcd(r,r*)", "s", "IC факт.", "IC оцінка"],
               tablefmt="github"))

# ---------------------------------------------------------------------------
# 3. Відновлення ключа
# ---------------------------------------------------------------------------
print(f"\n--- Завдання 3. Відновлення ключа (r = {best_r}) ---")
blocks = get_blocks(ciphertext, best_r)
chi_key = recover_key_chisquare(ciphertext, best_r)

top_x = "оеа"  # найімовірніші літери мови (з ЛР1: о, е, а)
rows = []
naive = []
for i, b in enumerate(blocks):
    y, cnt = Counter(b).most_common(1)[0]
    ks = [IDX_TO_CHAR[(CHAR_TO_IDX[y] - CHAR_TO_IDX[x]) % M] for x in top_x]
    naive.append(ks[0])
    rows.append([i, y, cnt, len(b), *ks, chi_key[i]])
print(tabulate(rows, headers=["i", "y*", "N(y*)", "|Y_i|",
                              "k (x*=о)", "k (x*=е)", "k (x*=а)", "chi^2"],
               tablefmt="github"))

naive_key = "".join(naive)
print(f"\nКлюч за x* = «о» для всіх блоків: {naive_key}")
print(f"Ключ за критерієм хі-квадрат:     {chi_key}")
diff_pos = [i for i in range(best_r) if naive_key[i] != chi_key[i]]
print(f"Позиції, де x* = «о» не спрацював: {diff_pos}")

final_key = chi_key  # без ручної підміни
plaintext = decrypt(ciphertext, final_key)
with open("data/decrypted_v10.txt", "w", encoding="utf-8") as f:
    f.write(plaintext)

print(f"\nЗнайдений ключ: {final_key}")
print(f"I(розшифрований текст) = {calc_ic(plaintext):.5f} "
      f"(I мови = {I_LANG:.5f}) -> перевірка ключа без знання ВТ")
print(f"Початок:  {plaintext[:200]}...")
print(f"Кінець:   ...{plaintext[-120:]}")

# Перевірка по вікнах: якщо десь «з'їхала» фаза ключа (помилка в шифртексті),
# I вікна різко впаде до ~0.031.
W = 400
win = [calc_ic(plaintext[s:s + W]) for s in range(0, n - W + 1, W)]
print(f"I по вікнах по {W} символів: min = {min(win):.4f}, max = {max(win):.4f}")
if min(win) < 0.042:
    print("УВАГА: є вікна з I ~ випадковим текстом - перевірте цілісність "
          "шифртексту (пропущені/спотворені символи).")

# ---------------------------------------------------------------------------
# 4. Помилка в одному символі ключа
# ---------------------------------------------------------------------------
print("\n--- Завдання 4. Помилка в одному символі ключа ---")
pos = 0
wrong_char = "а" if final_key[pos] != "а" else "б"
err_key = final_key[:pos] + wrong_char + final_key[pos + 1:]
shift = (CHAR_TO_IDX[final_key[pos]] - CHAR_TO_IDX[wrong_char]) % M  # на скільки зсунеться ВТ

print("ПРОГНОЗ (до експерименту):")
print(f"  - ключ має r = {best_r} символів, змінений символ №{pos}: "
      f"«{final_key[pos]}» -> «{wrong_char}»;")
print(f"  - зіпсуються лише позиції i, де i mod {best_r} = {pos}: "
      f"приблизно n/r = {n / best_r:.0f} літер ({100 / best_r:.1f}%);")
print(f"  - усі вони зміщені на однакову величину "
      f"+{shift} mod {M} (різниця символів ключа); решта тексту не зміниться.")

err_plain = decrypt(ciphertext, err_key)
diff = [i for i in range(n) if plaintext[i] != err_plain[i]]
shifts = {(CHAR_TO_IDX[err_plain[i]] - CHAR_TO_IDX[plaintext[i]]) % M
          for i in diff}
print("\nРЕЗУЛЬТАТ:")
print(f"  ключ:  {final_key}\n  помилк: {err_key}")
print(f"  змінено літер: {len(diff)} з {n} ({100 * len(diff) / n:.2f}%)")
print(f"  усі на позиціях i mod {best_r} = {sorted({i % best_r for i in diff})}")
print(f"  зсув змінених літер (mod {M}): {sorted(shifts)}")
print(f"  правильно: {plaintext[:100]}")
print(f"  з помилкою: {err_plain[:100]}")
print(f"  I(з помилкою) = {calc_ic(err_plain):.5f}")
