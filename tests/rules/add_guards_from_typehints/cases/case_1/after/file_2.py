def add(a: int, b: int) -> int:
    if not all([isinstance(a, int), isinstance(b, int)]):
        raise TypeError(f"Invalid arg types:\n`a` expected `int` got `{type(a)}`\n`b` expected `int` got `{type(b)}`")
    return a + b


def new_sum(value_1: int, value_2: int) -> int:
    if not all([isinstance(value_1, int), isinstance(value_2, int)]):
        raise TypeError(
            f"Invalid arg types:\n`value_1` expected `int` got `{type(value_1)}`\n`value_2` expected `int` got `{type(value_2)}`"
        )
    return value_1 + value_2
