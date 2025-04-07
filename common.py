# common.py
import random
import string


def generate_random_data(n):
    """
    Generuje listę n krotek (name, value) z losowymi danymi.
    """
    data = []
    for _ in range(n):
        name = "".join(random.choices(string.ascii_letters, k=10))
        value = random.randint(1, 1000)
        data.append((name, value))
    return data
