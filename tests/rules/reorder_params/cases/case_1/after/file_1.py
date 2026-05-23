from .file_2 import func


def main() -> None:
    func(2.0, "a", 0)
    func(c=3.0, b="b", a=2)
    func(c=4.0, b="c", a=4)
