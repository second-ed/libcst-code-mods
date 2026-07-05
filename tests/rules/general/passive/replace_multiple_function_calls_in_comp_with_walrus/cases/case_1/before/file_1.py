from collections.abc import Callable, Iterable
from typing import Any


def should_replace_multiple_function_calls_with_walrus(xs: Iterable, f: Callable) -> list[Any]:
    return [f(x) for x in xs if f(x)]
