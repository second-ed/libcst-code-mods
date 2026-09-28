from functools import lru_cache

import attrs
from dataclasses import dataclass


class SomeVanillaClass:
    pass


@dataclass(slots=True, frozen=True)
class SomeDataclass:
    pass


@attrs.define(frozen=True)
class SomeAttrsClass:
    pass


@lru_cache
def some_unchanged_function_with_decorator() -> None:
    pass
