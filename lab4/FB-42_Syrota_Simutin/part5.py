import random
from pathlib import Path

from part4 import load_keys, Encrypt, Decrypt, Sign, Verify


def SendKey(k, sender_private_key, receiver_public_key):
    _, p, q = sender_private_key
    n = p * q
    n1, _ = receiver_public_key

    if not 0 < k < n:
        raise ValueError("Ключ має задовольняти 0 < k < n")

    if n > n1:
        raise ValueError("Модуль відправника має бути не більшим за модуль отримувача")

    signature = Sign(k, sender_private_key)

    encrypted_key = Encrypt(k, receiver_public_key)
    encrypted_signature = Encrypt(signature, receiver_public_key)

    return encrypted_key, encrypted_signature


def ReceiveKey(encrypted_key, encrypted_signature,
               receiver_private_key, sender_public_key):
    _, p1, q1 = receiver_private_key
    n1 = p1 * q1
    n, _ = sender_public_key

    if n > n1:
        raise ValueError("Порушено умову n <= n1")

    k = Decrypt(encrypted_key, receiver_private_key)
    signature = Decrypt(encrypted_signature, receiver_private_key)

    if not 0 < k < n:
        raise ValueError("Отриманий ключ поза допустимим діапазоном")

    if not Verify(k, signature, sender_public_key):
        raise ValueError("Підпис неправильний — ключ відхилено")

    return k, signature


if __name__ == "__main__":
    filename = Path(__file__).resolve().with_name("keys.txt")
    public_a, private_a, public_b, private_b = load_keys(filename)

    n, e = public_a
    n1, e1 = public_b

    k = random.randrange(1, n)

    print("ПРОТОКОЛ ПЕРЕДАЧІ КЛЮЧА A -> B")
    print("\nПеревірка n <= n1:", n <= n1)

    print("\nВІДПРАВНИК A")

    print("1. Випадковий ключ:")
    print("k =", k)

    signature = Sign(k, private_a)

    print("\n2. Підпис ключа секретним ключем A:")
    print("S = k^d mod n =", signature)

    encrypted_key, encrypted_signature = SendKey(
        k, private_a, public_b
    )

    print("\n3. Шифрування відкритим ключем B:")
    print("k1 = k^e1 mod n1 =", encrypted_key)
    print("S1 = S^e1 mod n1 =", encrypted_signature)

    print("\n4. Відкритим каналом передаємо пару (k1, S1):")
    print((encrypted_key, encrypted_signature))

    print("\nОТРИМУВАЧ B")

    received_key, received_signature = ReceiveKey(
        encrypted_key,
        encrypted_signature,
        private_b,
        public_a,
    )

    print("\n5. Розшифрування секретним ключем B:")
    print("k = k1^d1 mod n1 =", received_key)
    print("S = S1^d1 mod n1 =", received_signature)

    recovered_value = Encrypt(received_signature, public_a)

    print("\n6. Перевірка підпису відкритим ключем A:")
    print("S^e mod n =", recovered_value)
    print("Підпис правильний:", Verify(
        received_key, received_signature, public_a
    ))

    print("\n7. Результат:")
    print("Отриманий ключ збігається з початковим:", received_key == k)

    print("\nПЕРЕВІРКА СПОТВОРЕНОГО ПАКЕТА")

    modified_signature = (encrypted_signature + 1) % n1

    try:
        ReceiveKey(
            encrypted_key,
            modified_signature,
            private_b,
            public_a,
        )
        print("Ключ прийнято")
    except ValueError as error:
        print("Ключ відхилено:", error)

    print("\nКонфіденційність:")
    print("Шифрування відкритим ключем B, розшифрування секретним ключем B.")

    print("\nПідтвердження справжності відправника:")
    print("Підпис секретним ключем A, перевірка відкритим ключем A.")