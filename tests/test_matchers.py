import libcst.matchers as m
import pytest
from libcst.metadata.wrapper import MetadataWrapper

import libcst_code_mods.matchers as mat
from libcst_code_mods.apply import get_manager
from libcst_code_mods.constants import REPO_ROOT
from libcst_code_mods.node_collector import NodeCollector, NodeMetadata

MATCHER_TEST_ROOT = f"{REPO_ROOT}/tests/test_examples"


@pytest.fixture(scope="session")
def test_manager():
    return get_manager(MATCHER_TEST_ROOT)


@pytest.fixture
def usecase_wrapper(test_manager, request: pytest.FixtureRequest) -> MetadataWrapper:
    return test_manager.get_metadata_wrapper_for_path(f"{MATCHER_TEST_ROOT}/{request.param}.py")


def _get_node_collecter_results(wrapper: MetadataWrapper, type_matcher: m.BaseMatcherNode) -> list[NodeMetadata]:
    collector = NodeCollector(type_matcher)
    wrapper.visit(collector)
    return collector.results


@pytest.mark.parametrize(
    ("usecase_wrapper", "expected_result"),
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
    indirect=["usecase_wrapper"],
)
def test_is_function(usecase_wrapper, expected_result):
    results = _get_node_collecter_results(usecase_wrapper, mat.is_function())
    assert bool(results) == expected_result


@pytest.mark.parametrize(
    ("usecase_wrapper", "expected_result"),
    [
        pytest.param(
            "function_nested_function",
            True,
            id="ensure matches on function",
        ),
        pytest.param(
            "function_single_line",
            False,
            id="ensure does not match on not function",
        ),
    ],
    indirect=["usecase_wrapper"],
)
def test_is_nested_function(usecase_wrapper, expected_result):
    results = _get_node_collecter_results(usecase_wrapper, mat.is_nested_function())
    assert bool(results) == expected_result


@pytest.mark.parametrize(
    ("usecase_wrapper", "expected_result"),
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
    indirect=["usecase_wrapper"],
)
def test_is_class(usecase_wrapper, expected_result):
    results = _get_node_collecter_results(usecase_wrapper, mat.is_class())
    assert bool(results) == expected_result


@pytest.mark.parametrize(
    ("usecase_wrapper", "expected_result"),
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
    indirect=["usecase_wrapper"],
)
def test_raises_exception(usecase_wrapper, expected_result):
    results = _get_node_collecter_results(usecase_wrapper, mat.raises_exception())
    assert bool(results) == expected_result


@pytest.mark.parametrize(
    ("usecase_wrapper", "type_matcher", "expected_result"),
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
    indirect=["usecase_wrapper"],
)
def test_has_return_type(usecase_wrapper, type_matcher, expected_result):
    results = _get_node_collecter_results(usecase_wrapper, mat.has_return_type(type_matcher))
    assert bool(results) == expected_result


@pytest.mark.parametrize(
    ("usecase_wrapper", "type_matcher", "expected_result"),
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
    indirect=["usecase_wrapper"],
)
def test_assignment_has_type_hint(usecase_wrapper, type_matcher, expected_result):
    results = _get_node_collecter_results(usecase_wrapper, mat.assignment_has_type_hint(type_matcher))
    assert bool(results) == expected_result


@pytest.mark.parametrize(
    ("usecase_wrapper", "type_matcher", "expected_result"),
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
    indirect=["usecase_wrapper"],
)
def test_param_has_type_hint(usecase_wrapper, type_matcher, expected_result):
    results = _get_node_collecter_results(usecase_wrapper, mat.param_has_type_hint(type_matcher))
    assert bool(results) == expected_result


@pytest.mark.parametrize(
    ("usecase_wrapper", "type_matcher", "expected_result"),
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
    indirect=["usecase_wrapper"],
)
def test_is_call_with_name(usecase_wrapper, type_matcher, expected_result):
    results = _get_node_collecter_results(usecase_wrapper, mat.is_call_with_name(type_matcher))
    assert bool(results) == expected_result


@pytest.mark.parametrize(
    ("usecase_wrapper", "type_matcher", "expected_result"),
    [
        pytest.param(
            "print_with_fstring",
            "x = ",
            True,
            id="ensure matches if text is present",
        ),
        pytest.param(
            "print_with_fstring",
            None,
            True,
            id="ensure matches if has any string element",
        ),
        pytest.param(
            "print_with_fstring",
            "blah blah",
            False,
            id="ensure does not match if string does not match",
        ),
    ],
    indirect=["usecase_wrapper"],
)
def test_is_fstring_with_text(usecase_wrapper, type_matcher, expected_result):
    results = _get_node_collecter_results(usecase_wrapper, mat.is_fstring_with_text(type_matcher))
    assert bool(results) == expected_result


@pytest.mark.parametrize(
    ("usecase_wrapper", "type_matcher", "expected_result"),
    [
        pytest.param(
            "print_with_fstring",
            m.Name("x"),
            True,
            id="ensure matches if text is present",
        ),
        pytest.param(
            "print_with_fstring",
            None,
            True,
            id="ensure matches if has any string element",
        ),
        pytest.param(
            "print_with_fstring",
            m.Name("blah blah"),
            False,
            id="ensure does not match if string does not match",
        ),
    ],
    indirect=["usecase_wrapper"],
)
def test_is_fstring_with_placeholder(usecase_wrapper, type_matcher, expected_result):
    results = _get_node_collecter_results(usecase_wrapper, mat.is_fstring_with_placeholder(type_matcher))
    assert bool(results) == expected_result
