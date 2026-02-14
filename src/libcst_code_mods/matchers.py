from __future__ import annotations

import libcst.matchers as m


def is_function() -> m.FunctionDef:
    return m.FunctionDef()


def is_class() -> m.ClassDef:
    return m.ClassDef()


def raises_exception(exc: m.BaseMatcherNode | None = None) -> m.BaseMatcherNode:
    exc = exc or m.DoNotCare()
    return m.FunctionDef(
        body=m.MatchIfTrue(
            lambda node: bool(
                m.findall(
                    node,
                    m.Raise(exc=m.DoNotCare()),
                )
            )
        )
    )


def has_return_type(annotation: m.BaseMatcherNode | None = None) -> m.FunctionDef:
    annotation = annotation or m.DoNotCare()
    return m.FunctionDef(returns=m.Annotation(annotation=annotation))
