def func(a: int, b: list[int] | None = None) -> None:
    b = b if b is not None else []
    pass


def func_2(a: int, b: dict | None = None) -> None:
    b = b if b is not None else {}
    pass


def func_3(a: int, b: set | None = None) -> None:
    b = b if b is not None else set()
    pass


def func_4(a: int, b: list | None = None) -> None:
    b = b if b is not None else []
    pass


func(2)
