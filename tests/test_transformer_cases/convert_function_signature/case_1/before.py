def add(a: int, b: int) -> int:
    return a + b


def new_sum(value_1: int, value_2: int) -> int:
    return value_1 + value_2


def main():
    x = add(1, 2)
    y = add(2, b=2)
    print(y)
    return x + y + add(a=-1, b=-1)
