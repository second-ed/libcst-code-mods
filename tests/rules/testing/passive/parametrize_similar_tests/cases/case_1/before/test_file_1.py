from operator import truediv


def add(a: int, b: int) -> int:
    return a + b


def sub(a: int, b: int) -> int:
    return a - b


def test_add_two_positive_numbers() -> None:
    a = 1
    b = 2
    assert add(a, b) == 3


def test_add_zero() -> None:
    a = 1
    b = 0
    assert add(a, b) == 1


def test_unrelated_function() -> None:
    a = 1
    b = 0
    assert sub(a, b) == 1


def test_div_with_positive_numbers() -> None:
    a = 12
    b = 3
    assert truediv(a, b) == 4, f"should never fail {a = } {b = }"


def test_div_with_negative_numbers() -> None:
    a = -6
    b = -2
    assert truediv(a, b) == -3, f"some other msg {a = } {b = }"


def test_div_with_mix_of_positive_and_negative() -> None:
    a = 12
    b = -3
    assert truediv(a, b) == -4
