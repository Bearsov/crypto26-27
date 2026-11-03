from part1 import generate_prime


def generate_pair(bits=256):
    p, _ = generate_prime(bits)
    q, _ = generate_prime(bits)

    while q == p:
        q, _ = generate_prime(bits)

    return p, q


def generate_two_pairs(bits=256):
    p, q = generate_pair(bits)
    p1, q1 = generate_pair(bits)

    if p * q > p1 * q1:
        p, q, p1, q1 = p1, q1, p, q

    return p, q, p1, q1


if __name__ == "__main__":
    p, q, p1, q1 = generate_two_pairs(256)

    print("Абонент A:")
    print("p =", p)
    print("q =", q)

    print("\nАбонент B:")
    print("p1 =", p1)
    print("q1 =", q1)

    print("\nБітові довжини:")
    for name, value in (("p", p), ("q", q), ("p1", p1), ("q1", q1)):
        print(f"{name}: {value.bit_length()} біт")

    print("\nДобутки:")
    print("p * q =", p * q)
    print("p1 * q1 =", p1 * q1)

    print("\nПеревірка p * q <= p1 * q1:")
    print(p * q <= p1 * q1)