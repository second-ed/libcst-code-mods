def add(a: int, b: int) -> int:
    if not all([isinstance(a, int), isinstance(b, int)]):
        raise TypeError(f"Invalid arg types:\n`a` expected `int` got `{type(a)}`\n`b` expected `int` got `{type(b)}`")
    return a + b


def new_sum(value_1: int, value_2: int) -> int:
    return value_1 + value_2
