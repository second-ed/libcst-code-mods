def func(a: int, b: str, c: float) -> str:
    logger.debug(f"{a = } {b = } {c = } ")
    if a % 2 == 0:
        return b + str(c)
    return str(c)
