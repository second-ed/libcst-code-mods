def add(a: int, b: int) -> int:
    return a + b


def new_sum(value_1: int, value_2: int) -> int:
    return value_1 + value_2


def main():
    x = new_sum(value_1=1, value_2=2)
    y = new_sum(value_1=2, value_2=2)
    print(y)
    return x + y + new_sum(value_1=-1, value_2=-1)
