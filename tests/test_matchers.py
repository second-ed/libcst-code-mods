import libcst as cst
import libcst.matchers as m
import pytest

import src.libcst_code_mods.matchers as mat


@pytest.mark.parametrize(
    ("fixture_get_matcher_case", "expected_result"),
    [
        pytest.param(
            "function_single_line",
            True,
            id="ensure matches on function",
        ),
        pytest.param(
            "global_assignment",
            False,
            id="ensure does not match on not function",
        ),
    ],
    indirect=["fixture_get_matcher_case"],
)
def test_is_function(fixture_get_matcher_case, expected_result):
    code = fixture_get_matcher_case
    node = cst.parse_module(code).body[0]
    assert m.matches(node, mat.is_function()) == expected_result


@pytest.mark.parametrize(
    ("fixture_get_matcher_case", "expected_result"),
    [
        pytest.param(
            "class_single_method",
            True,
            id="ensure matches on class",
        ),
        pytest.param(
            "function_single_line",
            False,
            id="ensure does not match on not other elem",
        ),
    ],
    indirect=["fixture_get_matcher_case"],
)
def test_is_class(fixture_get_matcher_case, expected_result):
    code = fixture_get_matcher_case
    node = cst.parse_module(code).body[0]
    assert m.matches(node, mat.is_class()) == expected_result


@pytest.mark.parametrize(
    ("fixture_get_matcher_case", "expected_result"),
    [
        pytest.param(
            "function_raises_exception",
            True,
            id="ensure matches if function raises",
        ),
        pytest.param(
            "function_nested_raises",
            True,
            id="ensure matches if function raises in if block",
        ),
        pytest.param(
            "function_single_line",
            False,
            id="ensure does not match if does not raise",
        ),
    ],
    indirect=["fixture_get_matcher_case"],
)
def test_raises_exception(fixture_get_matcher_case, expected_result):
    code = fixture_get_matcher_case
    node = cst.parse_module(code).body[0]
    assert m.matches(node, mat.raises_exception()) == expected_result


@pytest.mark.parametrize(
    ("fixture_get_matcher_case", "type_matcher", "expected_result"),
    [
        pytest.param(
            "function_single_line",
            m.Name("int"),
            True,
            id="ensure matches if has specified return type",
        ),
        pytest.param(
            "function_raises_exception",
            None,
            True,
            id="ensure matches if function has any return type",
        ),
        pytest.param(
            "function_raises_exception",
            m.Name("int"),
            False,
            id="ensure does not match if function does not have the specified return type",
        ),
    ],
    indirect=["fixture_get_matcher_case"],
)
def test_has_return_type(fixture_get_matcher_case, type_matcher, expected_result):
    code = fixture_get_matcher_case
    node = cst.parse_module(code).body[0]
    assert m.matches(node, mat.has_return_type(type_matcher)) == expected_result
