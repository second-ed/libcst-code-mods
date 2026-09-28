from functools import lru_cache

import attrs
from dataclasses import dataclass


class SomeVanillaClass:
    pass


@dataclass(frozen=True)
class SomeDataclass:
    pass


@dataclass(slots=True)
class SomeSlottedDataclass:
    pass


@attrs.define
class SomeAttrsClass:
    pass


@lru_cache
def some_unchanged_function_with_decorator() -> None:
    pass
