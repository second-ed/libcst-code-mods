from collections.abc import Callable, Iterable
from typing import Any


def should_replace_multiple_function_calls_with_walrus(xs: Iterable, f: Callable) -> list[Any]:
    return [f(x) for x in xs if f(x)]


def should_replace_multiple_function_calls_with_comparison_with_walrus(xs: Iterable, f: Callable) -> list[Any]:
    return [f(x) for x in xs if f(x) > 1]


def should_replace_multiple_function_calls_with_nested_call_in_cond(
    xs: Iterable, f: Callable, g: Callable
) -> list[Any]:
    return [f(x) for x in xs if g(f(x))]
