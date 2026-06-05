def func(a: int, b: str, c: float) -> str:
    if not all([isinstance(a, int), isinstance(b, str), isinstance(c, float)]):
        raise TypeError(
            f"Invalid arg types:\n`a` expected `int` got `{type(a)}`\n`b` expected `str` got `{type(b)}`\n`c` expected `float` got `{type(c)}`"
        )
    if a % 2 == 0:
        return b + str(c)
    return str(c)
