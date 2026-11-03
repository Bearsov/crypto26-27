"""
Модуль реалізації шифру Віженера та попередньої обробки текстів.
"""

ALPHABET = "абвгдежзийклмнопрстуфхцчшщъыьэюя"
M = len(ALPHABET)
CHAR_TO_IDX = {ch: i for i, ch in enumerate(ALPHABET)}
IDX_TO_CHAR = {i: ch for i, ch in enumerate(ALPHABET)}


def clean_text(text: str) -> str:
    """Очищає текст: приведення до нижнього регістру, заміна 'ё' на 'е' та фільтрація за алфавітом."""
    text = text.lower().replace("ё", "е")
    return "".join([c for c in text if c in CHAR_TO_IDX])


def encrypt(plaintext: str, key: str) -> str:
    """Зашифрування відкритого тексту шифром Віженера."""
    pt = clean_text(plaintext)
    k = clean_text(key)
    r = len(k)
    res = []
    for i, ch in enumerate(pt):
        x = CHAR_TO_IDX[ch]
        k_idx = CHAR_TO_IDX[k[i % r]]
        y = (x + k_idx) % M
        res.append(IDX_TO_CHAR[y])
    return "".join(res)


def decrypt(ciphertext: str, key: str) -> str:
    """Розшифрування шифртексту шифром Віженера."""
    ct = clean_text(ciphertext)
    k = clean_text(key)
    r = len(k)
    res = []
    for i, ch in enumerate(ct):
        y = CHAR_TO_IDX[ch]
        k_idx = CHAR_TO_IDX[k[i % r]]
        x = (y - k_idx) % M
        res.append(IDX_TO_CHAR[x])
    return "".join(res)