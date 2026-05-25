from functools import singledispatch

import libcst as cst
import libcst.matchers as m


@singledispatch
def to_matcher(node: cst.CSTNode) -> m.BaseMatcherNode | m.BaseExpressionMatchType | m.DoNotCareSentinel:
    raise NotImplementedError(f"to_matcher not implemented for type {type(node)}")


PRIMITIVES = {
    cst.Integer: m.Integer,
    cst.Float: m.Float,
    cst.SimpleString: m.SimpleString,
    cst.List: m.List,
    cst.Tuple: m.Tuple,
    cst.Set: m.Set,
    cst.Dict: m.Dict,
}


def register_primitives(node_type: cst.CSTNode, matcher_type: m.BaseMatcherNode) -> None:
    @to_matcher.register(node_type)
    def _(_node: cst.CSTNode) -> m.BaseMatcherNode:
        return matcher_type()


for k, v in PRIMITIVES.items():
    register_primitives(k, v)


@to_matcher.register(cst.Name)
def _(node: cst.Name) -> m.Name | m.DoNotCareSentinel:
    if node.value == "__cm_any__":
        return m.DoNotCare()
    return m.Name(node.value)


@to_matcher.register(cst.Attribute)
def _(node: cst.Attribute) -> m.Attribute:
    return m.Attribute(value=to_matcher(node.value), attr=to_matcher(node.attr))


@to_matcher.register(cst.Call)
def _(node: cst.Call) -> m.Call:
    return m.Call(to_matcher(node.func), args=[to_matcher(arg) for arg in node.args])


@to_matcher.register(cst.Arg)
def _(node: cst.Arg) -> m.Arg:
    if node.keyword is not None:
        return m.Arg(value=to_matcher(node.value), keyword=to_matcher(node.keyword))
    return m.Arg(value=to_matcher(node.value))
