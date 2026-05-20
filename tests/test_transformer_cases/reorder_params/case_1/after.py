def func(c: float, b: str, a: int) -> str:
    if a % 2 == 0:
        return b + str(c)
    return str(c)


def main() -> None:
    func(2.0, "a", 0)
    func(c=3.0, b="b", a=2)
    func(c=4.0, b="c", a=4)
