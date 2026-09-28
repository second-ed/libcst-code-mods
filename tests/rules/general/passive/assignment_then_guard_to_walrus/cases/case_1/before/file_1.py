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


def multiple_in_complex_condition() -> None:
    for i in range(10):
        a = fn(i)
        b = i + 1
        if a is None or b is None:
            continue


def should_avoid_walrus_assignment_within_generator(node: cst.FunctionDef, text: str) -> cst.FunctionDef | None:
    first_statement = node.body.body[0]
    comment = f"# {text}"
    if any(
        m.matches(line, m.EmptyLine(comment=m.Comment())) and line.comment.value == comment
        for line in first_statement.leading_lines
    ):
        return node


def should_not_use_walrus_if_would_result_in_multiple_fn_calls() -> int | None:
    fqn = expensive_fn(args)

    if fqn is None or not any(fqn in params for params in ("a", "b", "c")):
        return 0
