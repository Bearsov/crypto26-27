import os
import matplotlib.pyplot as plt
from src.attack import RUS_FREQS
from src.vigenere import clean_text
from src.stats import avg_ic_for_r, calc_dr

os.makedirs("plots", exist_ok=True)

with open("data/ciphertext_v10.txt", "r", encoding="utf-8") as f:
    ciphertext = clean_text(f.read())

I_LANG = sum(p * p for p in RUS_FREQS.values())
r_values = list(range(2, 31))
ic_values = [avg_ic_for_r(ciphertext, r) for r in r_values]
dr_values = [calc_dr(ciphertext, r) for r in r_values]

# 1. Графік Індексу відповідності
plt.figure(figsize=(10, 5))
plt.plot(r_values, ic_values, marker="o", color="navy", linewidth=2)
plt.axhline(y=I_LANG, color="r", linestyle="--",
            label=f"Теоретичний IC (російська мова ≈ {I_LANG:.4f})")
plt.axhline(y=1/32, color="g", linestyle=":", label="Випадковий IC (1/32 ≈ 0.03125)")
plt.title("Залежність середнього індексу відповідності від періоду r (Варіант 10)", fontsize=12)
plt.xlabel("Кандидат періоду r", fontsize=10)
plt.ylabel("Середній індекс відповідності (Avg IC)", fontsize=10)
plt.xticks(r_values)
plt.grid(True, linestyle="--", alpha=0.6)
plt.legend()
plt.tight_layout()
plt.savefig("plots/ic_dependence.png", dpi=300)
plt.close()

# 2. Графік Автокореляції D_r
plt.figure(figsize=(10, 5))
plt.bar(r_values, dr_values, color="teal", alpha=0.85)
plt.title("Статистика співпадінь D_r від відстані r (Варіант 10)", fontsize=12)
plt.xlabel("Відстань r", fontsize=10)
plt.ylabel("Кількість співпадінь D_r", fontsize=10)
plt.xticks(r_values)
plt.grid(True, linestyle="--", alpha=0.4, axis="y")
plt.tight_layout()
plt.savefig("plots/dr_dependence.png", dpi=300)
plt.close()

print("Графіки успішно збережено у папку plots/")
