from .file_1 import add


def main():
    x = add(1, 2)
    y = add(2, b=2)
    print(y)
    return x + y + add(a=-1, b=-1)
