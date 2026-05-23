from .file_1 import add


def main():
    x = new_sum(value_1=1, value_2=2)
    y = new_sum(value_1=2, value_2=2)
    print(y)
    return x + y + new_sum(value_1=-1, value_2=-1)
