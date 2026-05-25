from __future__ import annotations

import keyword
from operator import not_
import string

import hypothesis.strategies as st
import libcst as cst
import libcst.matchers as m
from hypothesis import given

from libcst_code_mods.rules._cst_to_matcher import to_matcher


def valid_text(inp_str: str) -> bool:
    return str.isidentifier(inp_str) and not keyword.iskeyword(inp_str)


IDENTIFIERS = st.text(alphabet=string.ascii_letters, min_size=1, max_size=20).filter(valid_text)


@given(IDENTIFIERS)
def test_to_matcher_name(name: str) -> None:
    node = cst.Name(name)
    matcher = to_matcher(node)

    assert m.matches(node, matcher)


@given(
    st.one_of(
        st.tuples(st.just(cst.Integer), st.integers(min_value=0).map(str)),
        st.tuples(st.just(cst.Float), st.floats(min_value=0, allow_nan=False, allow_infinity=False).map(str)),
        st.tuples(st.just(cst.SimpleString), st.text().map(repr)),
    )
)
def test_to_matcher_primitives(args) -> None:
    node_type, value = args
    node = node_type(value)
    assert m.matches(node, to_matcher(node))


@given(func_name=IDENTIFIERS, arg_name=IDENTIFIERS)
def test_to_matcher_call(func_name: str, arg_name: str) -> None:
    node = cst.Call(func=cst.Name(func_name), args=[cst.Arg(value=cst.Name(arg_name))])
    assert m.matches(node, to_matcher(node))


@given(left=IDENTIFIERS, right=IDENTIFIERS)
def test_to_matcher_attribute(left: str, right: str) -> None:
    node = cst.Attribute(value=cst.Name(left), attr=cst.Name(right))
    assert m.matches(node, to_matcher(node))


@given(left=IDENTIFIERS, middle=IDENTIFIERS, right=IDENTIFIERS)
def test_to_matcher_nested_attributes(left: str, middle: str, right: str) -> None:
    assert m.matches(
        cst.parse_expression(f"{left}.{middle}.{right}"),
        to_matcher(cst.parse_expression(f"{left}.{middle}.__cm_any__")),
    )


@given(func_name=IDENTIFIERS, kwarg=IDENTIFIERS, value=IDENTIFIERS)
def test_to_matcher_call_with_args(func_name: str, kwarg: str, value: str) -> None:
    node = cst.Call(func=cst.Name(func_name), args=[cst.Arg(keyword=cst.Name(kwarg), value=cst.Name(value))])
    assert m.matches(node, to_matcher(node))
