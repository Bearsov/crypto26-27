"""
Модуль автоматичного пошуку періоду r та відновлення символів ключа.
"""

from collections import Counter
from typing import Tuple, List
from .vigenere import ALPHABET, M, CHAR_TO_IDX, IDX_TO_CHAR
from .stats import avg_ic_for_r, calc_dr, get_blocks

# Стандартні частоти літер російської мови (32 літери)
RUS_FREQS = {
    'а': 0.0801, 'б': 0.0159, 'в': 0.0454, 'г': 0.0170, 'д': 0.0298,
    'е': 0.0845, 'ж': 0.0094, 'з': 0.0165, 'и': 0.0735, 'й': 0.0121,
    'к': 0.0349, 'л': 0.0440, 'м': 0.0321, 'н': 0.0670, 'о': 0.1097,
    'п': 0.0281, 'р': 0.0473, 'с': 0.0547, 'т': 0.0626, 'у': 0.0262,
    'ф': 0.0026, 'х': 0.0097, 'ц': 0.0048, 'ч': 0.0144, 'ш': 0.0073,
    'щ': 0.0036, 'ъ': 0.0004, 'ы': 0.0190, 'ь': 0.0174, 'э': 0.0032,
    'ю': 0.0064, 'я': 0.0201
}


def find_possible_periods(text: str, max_r: int = 30) -> List[Tuple[int, float, int]]:
    """Повертає список кандидатів періоду r із розрахованими середнім IC та D_r."""
    results = []
    for r in range(2, max_r + 1):
        ic_val = avg_ic_for_r(text, r)
        dr_val = calc_dr(text, r)
        results.append((r, ic_val, dr_val))
    return sorted(results, key=lambda x: x[1], reverse=True)


def recover_key_chisquare(text: str, r: int) -> str:
    """
    Відновлення ключа за допомогою критерію Хі-квадрат (Chi-Square test).
    Знаходить зсув, який мінімізує відхилення спостережуваних частот від теоретичних.
    """
    blocks = get_blocks(text, r)
    key = []

    for block in blocks:
        n = len(block)
        best_k = 0
        min_chisq = float('inf')

        for k in range(M):
            # Розшифровуємо блок зсувом k
            decrypted_indices = [(CHAR_TO_IDX[ch] - k) % M for ch in block]
            counts = Counter(decrypted_indices)

            chisq = 0.0
            for char, prob in RUS_FREQS.items():
                expected = n * prob
                observed = counts[CHAR_TO_IDX[char]]
                chisq += ((observed - expected) ** 2) / expected

            if chisq < min_chisq:
                min_chisq = chisq
                best_k = k

        key.append(IDX_TO_CHAR[best_k])

    return "".join(key)


def recover_key(text: str, r: int, target_char: str = "о") -> str:
    """Просте відновлення ключа за найчастішим символом (наївний метод)."""
    blocks = get_blocks(text, r)
    key = []
    target_idx = CHAR_TO_IDX[target_char]
    for block in blocks:
        most_common_char = Counter(block).most_common(1)[0][0]
        y_idx = CHAR_TO_IDX[most_common_char]
        k_idx = (y_idx - target_idx) % M
        key.append(IDX_TO_CHAR[k_idx])
    return "".join(key)