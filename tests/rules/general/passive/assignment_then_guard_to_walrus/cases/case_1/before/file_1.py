from typing import Any

import libcst as cst
import libcst.matchers as m


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


def multiple_to_change() -> None:
    if unrelated_condition:
        return

    res = fn()
    if res is None:
        return
    fn_2(res)

    res_2 = fn_2()
    if res_2 is not None:
        return res_2

    res_3 = fn_3()
    if not res_3:
        return
    fn_3_output(res_3)

    res_4 = fn_4()
    if res_4:
        return res_4


def make_slots_decorator(decorator: cst.Decorator) -> cst.Decorator:
    matched = m.extract(decorator, m.Decorator(decorator=m.SaveMatchedNode(m.Call(), "call")))
    if matched is None:
        return decorator
    return decorator.with_changes()
