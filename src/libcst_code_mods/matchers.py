from __future__ import annotations

import attrs
import libcst as cst
import libcst.matchers as m


@attrs.define(frozen=True)
class HasAny:
    match_cond: m.BaseMatcherNode

    def __call__(self, node: cst.CSTNode) -> bool:
        return bool(m.findall(node, self.match_cond))


def is_function() -> m.FunctionDef:
    return m.FunctionDef()


def is_class() -> m.ClassDef:
    return m.ClassDef()


def raises_exception(exc: m.BaseMatcherNode | None = None) -> m.BaseMatcherNode:
    exc = exc or m.DoNotCare()
    return m.FunctionDef(body=m.MatchIfTrue(HasAny(m.Raise(exc=exc))))


def has_return_type(type_hint: m.BaseMatcherNode | None = None) -> m.FunctionDef:
    type_hint = type_hint or m.DoNotCare()
    return m.FunctionDef(returns=m.Annotation(annotation=type_hint))


def assignment_has_type_hint(type_hint: m.BaseMatcherNode | None = None) -> m.BaseMatcherNode:
    type_hint = type_hint or m.DoNotCare()
    return m.AnnAssign(annotation=m.Annotation(annotation=type_hint))


def param_has_type_hint(type_hint: m.BaseMatcherNode | None = None) -> m.BaseMatcherNode:
    type_hint = type_hint or m.DoNotCare()
    return m.Param(annotation=m.Annotation(annotation=type_hint))
