from contextlib import nullcontext
from typing import ContextManager

import pytest
from package.file_1 import add, div


@pytest.mark.parametrize(("a", "b", "expected_result"), [pytest.param(0.0, 0.0, 0.0, id="given..., when..., then...")])
def test_add(a: float, b: float, expected_result: float) -> None:
    assert add(a, b) == expected_result


@pytest.mark.parametrize(
    ("a", "b", "expected_result", "expected_context"),
    [
        pytest.param(0.0, 0.0, 0.0, nullcontext(), id="given..., when..., then..."),
        pytest.param(
            0.0, 0.0, 0.0, pytest.raises(ZeroDivisionError), id="given..., when..., then should raise ZeroDivisionError"
        ),
    ],
)
def test_div(a: float, b: float, expected_result: float, expected_context: ContextManager) -> None:
    with expected_context:
        assert div(a, b) == expected_result
