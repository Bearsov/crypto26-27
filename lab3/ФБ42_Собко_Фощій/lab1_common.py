from collections import Counter
def bigram_freqs(text, overlapping=False):
    step = 1 if overlapping else 2
    return Counter(text[i:i+2] for i in range(0, len(text) - 1, step))
def top_n(counts, n=5):
    return counts.most_common(n)

