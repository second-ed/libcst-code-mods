from operator import truediv

import pytest


def add(a: int, b: int) -> int:
    return a + b


def sub(a: int, b: int) -> int:
    return a - b


@pytest.mark.parametrize(
    ("a", "b", "expected_result"),
    [pytest.param(1, 2, 3, id="add two positive numbers"), pytest.param(1, 0, 1, id="add zero")],
)
def test_add(a, b, expected_result) -> None:
    assert add(a, b) == expected_result


def test_unrelated_function() -> None:
    a = 1
    b = 0
    assert sub(a, b) == 1


@pytest.mark.parametrize(
    ("a", "b", "expected_result", "assert_msg"),
    [
        pytest.param(12, 3, 4, f"should never fail a = 12 b = 3", id="div with positive numbers"),
        pytest.param(-6, -2, -3, f"some other msg a = -6 b = -2", id="div with negative numbers"),
        pytest.param(12, -3, -4, "no assertion message provided", id="div with mix of positive and negative"),
    ],
)
def test_div_with(a, b, expected_result, assert_msg) -> None:
    assert truediv(a, b) == expected_result, assert_msg
