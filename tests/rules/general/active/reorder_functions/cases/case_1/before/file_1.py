def a() -> None:
    b()


def c() -> None:
    pass


def b() -> None:
    c()
