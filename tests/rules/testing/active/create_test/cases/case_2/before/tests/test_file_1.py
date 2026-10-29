from contextlib import nullcontext
from typing import ContextManager

import pytest
from package.file_1 import div


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
