"""Some docstring"""

try:
    import pathlib
except ImportError:
    import os


def a() -> None:
    b()


def b() -> None:
    c()


def c() -> None:
    pass


if __name__ == "__main__":
    print("this is main")
