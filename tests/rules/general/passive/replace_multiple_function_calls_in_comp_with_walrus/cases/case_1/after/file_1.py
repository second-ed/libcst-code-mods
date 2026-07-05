from collections.abc import Callable, Iterable
from typing import Any


def should_replace_multiple_function_calls_with_walrus(xs: Iterable, f: Callable) -> list[Any]:
    return [__code_mod_tmp for x in xs if (__code_mod_tmp := f(x))]


def should_replace_multiple_function_calls_with_comparison_with_walrus(xs: Iterable, f: Callable) -> list[Any]:
    return [__code_mod_tmp for x in xs if (__code_mod_tmp := f(x)) > 1]
