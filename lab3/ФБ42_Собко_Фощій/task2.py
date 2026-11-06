from pathlib import Path
from common import read, clean, LANG_BIGRAMS
from lab1_common import bigram_freqs, top_n

BASE = Path(__file__).resolve().parent

for name in ('06.txt', 'V6.txt'):
    text = clean(read(BASE / name))
    counts = bigram_freqs(text)
    total = sum(counts.values())
    print(f'\n{name}: {len(text)} літер, {total} біграм')
    for bg, n in top_n(counts):
        print(f'{bg}: {n} ({n / total:.4f})')

reference = BASE / 'book.txt'
if reference.exists():
    counts = bigram_freqs(clean(read(reference)))
    total = sum(counts.values())
    order = [bg for bg, _ in counts.most_common()]
    print(f'\nЕталонний текст book.txt: {total} біграм')
    print('Топ-10 біграм:')
    for bg, n in top_n(counts, 10):
        print(f'{bg}: {n} ({n / total:.4f})')
    print('Біграми з методички:')
    for bg in LANG_BIGRAMS:
        print(f'{bg}: {counts[bg]} ({counts[bg] / total:.4f}), місце {order.index(bg) + 1 if bg in order else "відсутня"}')
else:
    print('\nbook.txt не знайдено: порівняння з еталоном пропущено')
