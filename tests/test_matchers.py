import libcst.matchers as m
import pytest

import libcst_code_mods.matchers as mat
from libcst_code_mods.apply import get_manager
from libcst_code_mods.constants import REPO_ROOT
from libcst_code_mods.node_collector import NodeCollector, NodeMetadata


def _get_node_collecter_results(usecase: str, type_matcher: m.BaseMatcherNode) -> list[NodeMetadata]:
    root = f"{REPO_ROOT}/tests/test_examples"
    wrapper = get_manager(root).get_metadata_wrapper_for_path(f"{root}/{usecase}.py")
    collector = NodeCollector(type_matcher)
    wrapper.visit(collector)
    return collector.results


@pytest.mark.parametrize(
    ("matcher_case", "expected_result"),
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
)
def test_is_function(matcher_case, expected_result):
    results = _get_node_collecter_results(matcher_case, mat.is_function())
    assert bool(results) == expected_result


@pytest.mark.parametrize(
    ("matcher_case", "expected_result"),
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
)
def test_is_class(matcher_case, expected_result):
    results = _get_node_collecter_results(matcher_case, mat.is_class())
    assert bool(results) == expected_result


@pytest.mark.parametrize(
    ("matcher_case", "expected_result"),
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
)
def test_raises_exception(matcher_case, expected_result):
    results = _get_node_collecter_results(matcher_case, mat.raises_exception())
    assert bool(results) == expected_result


@pytest.mark.parametrize(
    ("matcher_case", "type_matcher", "expected_result"),
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
)
def test_has_return_type(matcher_case, type_matcher, expected_result):
    results = _get_node_collecter_results(matcher_case, mat.has_return_type(type_matcher))
    assert bool(results) == expected_result


@pytest.mark.parametrize(
    ("matcher_case", "type_matcher", "expected_result"),
    [
        pytest.param(
            "global_assignment_with_type_hint",
            m.Name("int"),
            True,
            id="ensure matches if has specified type hint",
        ),
        pytest.param(
            "global_assignment_with_type_hint",
            m.Name("float"),
            False,
            id="ensure does not match if does not have specified type hint",
        ),
        pytest.param(
            "global_assignment",
            None,
            False,
            id="ensure does not match if has no type hint",
        ),
    ],
)
def test_assignment_has_type_hint(matcher_case, type_matcher, expected_result):
    results = _get_node_collecter_results(matcher_case, mat.assignment_has_type_hint(type_matcher))
    assert bool(results) == expected_result


@pytest.mark.parametrize(
    ("matcher_case", "type_matcher", "expected_result"),
    [
        pytest.param(
            "function_single_line",
            m.Name("int"),
            True,
            id="ensure matches if has specified type hint",
        ),
        pytest.param(
            "function_single_line",
            m.Name("float"),
            False,
            id="ensure does not match if does not has specified type hint",
        ),
        pytest.param(
            "function_raises_exception",
            None,
            False,
            id="ensure does not match if has no type hint",
        ),
    ],
)
def test_param_has_type_hint(matcher_case, type_matcher, expected_result):
    results = _get_node_collecter_results(matcher_case, mat.param_has_type_hint(type_matcher))
    assert bool(results) == expected_result


@pytest.mark.parametrize(
    ("matcher_case", "type_matcher", "expected_result"),
    [
        pytest.param(
            "calls_print",
            m.Name("print"),
            True,
            id="ensure matches if calls specified function",
        ),
        pytest.param(
            "calls_print",
            None,
            True,
            id="ensure matches if has any call",
        ),
        pytest.param(
            "function_single_line",
            None,
            False,
            id="ensure does not match if has no call",
        ),
    ],
)
def test_is_call_with_name(matcher_case, type_matcher, expected_result):
    results = _get_node_collecter_results(matcher_case, mat.is_call_with_name(type_matcher))
    assert bool(results) == expected_result
