# Комп'ютерний практикум №4 — RSA, електронний підпис, генерація простих чисел

Бригада: ФБ-43, Горбонос О., Дрєпіна А.

## Структура

```
code/       rsa.py (усі функції), task1…task5, verify.py
data/       server_session.json (протокол обміну з тестовим середовищем)
results/    primes.json, keys.json, messages.json, protocol.json, server_check.json
artifacts/  скріншоти тестового середовища
report/     KP4_zvit.docx, KP4_zvit.pdf
```

`results/keys.json` містить секретні ключі, бо це навчальні дані для звіту. Для реальних ключів так робити не можна.

## Запуск

Потрібен Python 3.9+. Сама реалізація не має зовнішніх залежностей, `sympy` потрібен лише для `verify.py`:
`pip install -r requirements.txt`. Порядок запуску важливий:

```bash
cd code
python task1_primes.py
python task2_keys.py
python task3_messages.py
python task4_protocol.py
python task5_server.py
python verify.py
```

Зафіксований `seed` дає ті самі числа під час повторного запуску.

`task5_server.py` не звертається до сервера: він перераховує локальну частину операцій і звіряє її з відповідями із `data/server_session.json`. Якщо змінити `seed` або ключі, цей файл перестане їм відповідати, і обмін із сервером треба буде повторити.

Команда `python task5_server.py prepare <n_512> <e_512> <n_1024> <e_1024>` обчислює значення, які вводяться у форми сервера (числа в hex).
