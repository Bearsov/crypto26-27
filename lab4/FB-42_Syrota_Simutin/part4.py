import random
from pathlib import Path

from part1 import mod_pow


def load_keys(filename):
    values = {}

    with open(filename, "r", encoding="utf-8") as file:
        for line in file:
            if line.strip():
                name, value = line.split("=", 1)
                values[name.strip()] = int(value.strip())

    public_a = (values["n"], values["e"])
    private_a = (values["d"], values["p"], values["q"])

    public_b = (values["n1"], values["e1"])
    private_b = (values["d1"], values["p1"], values["q1"])

    return public_a, private_a, public_b, private_b


def Encrypt(message, public_key):
    n, e = public_key

    if not 0 <= message < n:
        raise ValueError("Повідомлення має задовольняти 0 <= M < n")

    return mod_pow(message, e, n)


def Decrypt(ciphertext, private_key):
    d, p, q = private_key
    n = p * q

    if not 0 <= ciphertext < n:
        raise ValueError("Криптограма має задовольняти 0 <= C < n")

    return mod_pow(ciphertext, d, n)


def Sign(message, private_key):
    d, p, q = private_key
    n = p * q

    if not 0 <= message < n:
        raise ValueError("Повідомлення має задовольняти 0 <= M < n")

    return mod_pow(message, d, n)


def Verify(message, signature, public_key):
    n, e = public_key

    if not 0 <= message < n or not 0 <= signature < n:
        return False

    return mod_pow(signature, e, n) == message


if __name__ == "__main__":
    filename = Path(__file__).resolve().with_name("keys.txt")
    public_a, private_a, public_b, private_b = load_keys(filename)

    message = random.randrange(1, min(public_a[0], public_b[0]))

    print("ВІДКРИТЕ ПОВІДОМЛЕННЯ")
    print("M =", message)

    print("\nШИФРУВАННЯ ДЛЯ АБОНЕНТА A")

    ciphertext_a = Encrypt(message, public_a)
    decrypted_a = Decrypt(ciphertext_a, private_a)

    print("C_A = M^e mod n =", ciphertext_a)
    print("M_A = C_A^d mod n =", decrypted_a)
    print("M_A == M:", decrypted_a == message)

    print("\nШИФРУВАННЯ ДЛЯ АБОНЕНТА B")

    ciphertext_b = Encrypt(message, public_b)
    decrypted_b = Decrypt(ciphertext_b, private_b)

    print("C_B = M^e1 mod n1 =", ciphertext_b)
    print("M_B = C_B^d1 mod n1 =", decrypted_b)
    print("M_B == M:", decrypted_b == message)

    print("\nЦИФРОВИЙ ПІДПИС АБОНЕНТА A")

    signature_a = Sign(message, private_a)
    signed_message_a = (message, signature_a)

    print("S_A = M^d mod n =", signature_a)
    print("Підписане повідомлення (M, S_A):")
    print(signed_message_a)
    print("Підпис A правильний:", Verify(*signed_message_a, public_a))

    print("\nЦИФРОВИЙ ПІДПИС АБОНЕНТА B")

    signature_b = Sign(message, private_b)
    signed_message_b = (message, signature_b)

    print("S_B = M^d1 mod n1 =", signature_b)
    print("Підписане повідомлення (M, S_B):")
    print(signed_message_b)
    print("Підпис B правильний:", Verify(*signed_message_b, public_b))

    print("\nПЕРЕВІРКА ЗМІНЕНОГО ПОВІДОМЛЕННЯ")

    modified_message = message - 1

    print("Змінене M =", modified_message)
    print("Перевірка підпису A:", Verify(
        modified_message, signature_a, public_a
    ))
    print("Перевірка підпису B:", Verify(
        modified_message, signature_b, public_b
    ))