def func(a: int, b: str = "b", c: float = 0.0) -> str:
    if a % 2 == 0:
        return b + str(c)
    return str(c)
