from typing import Any


def checks_if_is_none() -> None:
    if (res := fn()) is None:
        return
    fn_2(res)


def checks_if_is_not_none() -> Any:
    if (res := fn()) is not None:
        return res


def checks_if_is_not_truthy() -> None:
    if not (res := fn()):
        return
    fn_2(res)


def checks_if_is_truthy() -> Any | None:
    if res := fn():
        return res
