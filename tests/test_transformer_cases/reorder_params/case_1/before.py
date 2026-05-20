def func(a: int, b: str, c: float) -> str:
    if a % 2 == 0:
        return b + str(c)
    return str(c)


def main() -> None:
    func(0, "a", 2.0)
    func(2, b="b", c=3.0)
    func(a=4, b="c", c=4.0)
