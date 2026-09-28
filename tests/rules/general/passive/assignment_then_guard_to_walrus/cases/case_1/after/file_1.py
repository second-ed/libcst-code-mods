from typing import Any

import libcst as cst
import libcst.matchers as m


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


def multiple_to_change() -> None:
    if unrelated_condition:
        return

    if (res := fn()) is None:
        return
    fn_2(res)

    if (res_2 := fn_2()) is not None:
        return res_2

    if not (res_3 := fn_3()):
        return
    fn_3_output(res_3)

    if res_4 := fn_4():
        return res_4


def make_slots_decorator(decorator: cst.Decorator) -> cst.Decorator:
    if (matched := m.extract(decorator, m.Decorator(decorator=m.SaveMatchedNode(m.Call(), "call")))) is None:
        return decorator
    return decorator.with_changes()
