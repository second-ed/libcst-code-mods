from .file_2 import func


def main() -> None:
    func(0, "a", 2.0)
    func(2, c=3.0, b="b")
    func(a=4, b="c", c=4.0)
