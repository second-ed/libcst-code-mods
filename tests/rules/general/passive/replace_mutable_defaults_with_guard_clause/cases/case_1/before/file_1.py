def func(a: int, b: list[int] = []) -> list[int]:
    """some docstring"""
    x = 1
    b.extend([a, x])
    return b


def func_2(a: int, b: dict = {}) -> None:
    pass


def func_3(a: int, b: set = set()) -> None:
    pass


def func_4(a: int, b: list = list()) -> None:
    pass


def kw_only_mutable_default(a: dict = {}, /, *, b: list[int] = []) -> None:
    pass


func(2)
