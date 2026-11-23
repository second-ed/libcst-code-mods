"""Some docstring"""

try:
    import pathlib
except ImportError:
    import os


def a() -> None:
    b()


def c() -> None:
    pass


def b() -> None:
    c()


if __name__ == "__main__":
    print("this is main")
