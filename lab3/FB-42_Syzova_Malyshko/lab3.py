import collections
# Завдання 1. Математичний апарат
def egcd(a, b):
    if a == 0:
        return (b, 0, 1)
    else:
        g, y, x = egcd(b % a, a)
        return (g, x - (b // a) * y, y)

def mod_inverse(a, m):
    g, x, y = egcd(a, m)
    if g != 1:
        return None
    return x % m

def solve_linear_congruence(a, b, n):
    g, x, y = egcd(a, n)
    if b % g != 0:
        return []
    a1, b1, n1 = a // g, b // g, n // g
    inv_a1 = mod_inverse(a1, n1)
    if inv_a1 is None:
        return []
    x0 = (b1 * inv_a1) % n1
    return [(x0 + i * n1) % n for i in range(g)]


# Завдання 2. Підрахунок частих біграм
def get_top_bigrams(filename, top_n=5):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            text = f.read().replace('\n', '').replace('\r', '').replace(' ', '')
        
        bigrams = [text[i:i+2] for i in range(0, len(text)-1, 2)]
        
        counter = collections.Counter(bigrams)
        return counter.most_common(top_n)
    except FileNotFoundError:
        return f"Помилка: файл {filename} не знайдено."

if __name__ == "__main__":
    filename = "02.txt"  
    
    print(f"Аналіз файлу {filename}...\n")
    top_5 = get_top_bigrams(filename, 5)
    
    if isinstance(top_5, str):
        print(top_5)
    else:
        print("Топ-5 біграм шифртексту:")
        for rank, (bg, count) in enumerate(top_5, 1):
            print(f"{rank}. '{bg}' : {count}") 
