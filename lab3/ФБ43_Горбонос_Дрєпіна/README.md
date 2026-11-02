# Комп'ютерний практикум №3 — Криптоаналіз афінної біграмної підстановки

Бригада: ФБ-43, Горбонос О., Дрєпіна А. Варіант 2.

## Структура

```
code/       affine.py (спільний модуль), task1…task4, verify.py
data/       variant2_cipher.txt, for_test/, kp1/ (текст і частоти з КП1)
results/    таблиці, JSON, decrypted.txt, key.txt
artifacts/  графік розпізнавача
report/     KP3_zvit.docx, KP3_zvit.pdf
```

## Запуск

Потрібні Python 3.9+ і `pip install -r requirements.txt`. Шляхи рахуються від розташування
скриптів, тому запускати можна з будь-якої папки. Порядок важливий:

```bash
cd code
python task1_math.py
python task2_bigrams.py
python task3_candidates.py
python task4_recognizer.py
python verify.py
```

`task3` читає результат `task2`, `verify` читає результати `task2` і `task4`.

## Результат

Ключ: a = 27, b = 211. Алфавіт: `абвгдежзийклмнопрстуфхцчшщьыэюя` (ь = 26, ы = 27).
У файлах `for_test` порядок інший: `…щыьэюя`.
