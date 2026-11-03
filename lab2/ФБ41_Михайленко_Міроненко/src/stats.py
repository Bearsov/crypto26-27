"""
Модуль розрахунку статистичних показників (Індекс відповідності, Автокореляція D_r).
"""

from collections import Counter
from typing import List
from .vigenere import ALPHABET, M, CHAR_TO_IDX


def calc_ic(text: str) -> float:
    """
    Обчислення індексу відповідності (Index of Coincidence) для тексту.
    Формула: I(Y) = sum(N_t * (N_t - 1)) / (N * (N - 1))
    """
    n = len(text)
    if n <= 1:
        return 0.0
    counts = Counter(text)
    num = sum(f * (f - 1) for f in counts.values())
    return num / (n * (n - 1))


def calc_dr(text: str, r: int) -> int:
    """
    Обчислення статистики співпадінь символів на відстані r (Автокореляція).
    Формула: D_r = sum(delta(y_i, y_{i+r}))
    """
    return sum(1 for i in range(len(text) - r) if text[i] == text[i + r])


def get_blocks(text: str, r: int) -> List[str]:
    """Розбиття тексту на r моноалфавітних блоків Y_0, Y_1, ..., Y_{r-1}."""
    return [text[i::r] for i in range(r)]


def avg_ic_for_r(text: str, r: int) -> float:
    """Усереднений індекс відповідності по всіх r блоках."""
    blocks = get_blocks(text, r)
    return sum(calc_ic(b) for b in blocks) / r