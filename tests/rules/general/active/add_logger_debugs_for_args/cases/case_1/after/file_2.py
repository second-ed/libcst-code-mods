def add(a: int, b: int) -> int:
    return a + b


def new_sum(value_1: int, value_2: int) -> int:
    logger.debug(f"{value_1 = } {value_2 = } ")
    return value_1 + value_2


def big_func(a: int, b: list[str], c: dict[int, str], d: set[float]) -> None:
    pass
