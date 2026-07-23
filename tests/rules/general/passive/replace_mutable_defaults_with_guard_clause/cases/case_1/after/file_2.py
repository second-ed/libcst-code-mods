def big_func(
    a: int,
    b: list | None = None,
    c: dict | None = None,
    d: set | None = None,
    e: list | None = None,
    f: dict | None = None,
) -> None:
    b = b if b is not None else []
    c = c if c is not None else {}
    d = d if d is not None else set()
    e = e if e is not None else []
    f = f if f is not None else {}
    pass
