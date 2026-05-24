from functools import singledispatch

import libcst as cst
import libcst.matchers as m


@singledispatch
def to_matcher(node: cst.CSTNode) -> m.BaseMatcherNode | m.DoNotCareSentinel:
    raise NotImplementedError(f"to_matcher not implemented for type {type(node)}")


@to_matcher.register(cst.Name)
def _(node: cst.Name) -> m.Name | m.DoNotCareSentinel:
    if node.value == "__cm_any__":
        return m.DoNotCare()
    return m.Name(node.value)


@to_matcher.register(cst.Attribute)
def _(node: cst.Attribute) -> m.Name | m.DoNotCareSentinel:
    return m.Attribute(value=to_matcher(node.value), attr=to_matcher(node.attr))
