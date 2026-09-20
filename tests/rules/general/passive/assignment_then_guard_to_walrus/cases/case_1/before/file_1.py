from typing import Any


def checks_if_is_none() -> None:
    res = fn()
    if res is None:
        return
    fn_2(res)


def checks_if_is_not_none() -> Any:
    res = fn()
    if res is not None:
        return res


def checks_if_is_not_truthy() -> None:
    res = fn()
    if not res:
        return
    fn_2(res)


def checks_if_is_truthy() -> Any | None:
    res = fn()
    if res:
        return res
