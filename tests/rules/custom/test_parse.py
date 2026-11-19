import pytest
import libcst.matchers as m
import libcst as cst

from libcst_code_mods.rules.custom.parse import _parse_matcher, _matcher_to_dict


@pytest.mark.parametrize(
    ("config", "expected_result", "should_match", "should_not_match"),
    [
        pytest.param(
            {"type": "Call", "func": {"type": "Name", "value": "print"}},
            m.Call(m.Name("print")),
            "print('blah')",
            "len([])",
        ),
        pytest.param(
            {
                "type": "Call",
                "func": {
                    "type": "OneOf",
                    "options": [
                        {"type": "Name", "value": "print"},
                        {"type": "Attribute", "attr": {"type": "Name", "value": "write"}},
                    ],
                },
            },
            m.Call(func=m.OneOf(m.Name(value="print"), m.Attribute(attr=m.Name(value="write")))),
            "thing.write()",
            "len([])",
        ),
        pytest.param(
            {
                "type": "Attribute",
                "value": {"type": "Call", "func": {"type": "Name", "value": "get_client"}},
                "attr": {"type": "Name", "value": "execute"},
            },
            m.Attribute(m.Call(m.Name("get_client")), attr=m.Name("execute")),
            "get_client().execute",
            "len([])",
        ),
    ],
)
def test_parse_matcher_for_expressions(config, expected_result, should_match, should_not_match) -> None:
    should_match_node = cst.parse_expression(should_match)

    assert m.matches(should_match_node, _parse_matcher(config))
    assert m.matches(should_match_node, expected_result)

    should_not_match_node = cst.parse_expression(should_not_match)

    assert not m.matches(should_not_match_node, _parse_matcher(config))
    assert not m.matches(should_not_match_node, expected_result)


@pytest.mark.parametrize(
    ("config", "expected_result", "should_match", "should_not_match"),
    [
        pytest.param(
            {
                "type": "SimpleStatementLine",
                "body": [
                    {
                        "type": "AnnAssign",
                        "target": {"type": "Name", "value": "result"},
                        "annotation": {"type": "Annotation", "annotation": {"type": "Name", "value": "str"}},
                        "value": {"type": "DoNotCare"},
                    }
                ],
            },
            m.SimpleStatementLine([m.AnnAssign(m.Name("result"), annotation=m.Annotation(m.Name("str")))]),
            "result: str = ''",
            "len([])",
        )
    ],
)
def test_parse_matcher_for_statements(config, expected_result, should_match, should_not_match) -> None:
    should_match_node = cst.parse_statement(should_match)

    assert m.matches(should_match_node, _parse_matcher(config)), (
        f"parsed matcher should correctly identify: {should_match_node}"
    )
    assert m.matches(should_match_node, expected_result), (
        f"expected matcher should correctly identify: {should_match_node}"
    )

    should_not_match_node = cst.parse_statement(should_not_match)

    assert not m.matches(should_not_match_node, _parse_matcher(config)), (
        f"parsed matcher should not identify: {should_not_match_node}"
    )
    assert not m.matches(should_not_match_node, expected_result), (
        f"expected matcher should not identify: {should_not_match_node}"
    )


@pytest.mark.parametrize(
    ("matcher", "node"),
    [
        pytest.param(m.Call(func=m.Name("print")), cst.parse_expression("print('x')")),
        pytest.param(
            m.Call(func=m.OneOf(m.Name("print"), m.Attribute(value=m.DoNotCare(), attr=m.Name("write")))),
            cst.parse_expression("thing.write()"),
        ),
        pytest.param(
            m.SimpleStatementLine(body=[m.AnnAssign(target=m.Name("result"), annotation=m.Annotation(m.Name("str")))]),
            cst.parse_statement("result: str = ''"),
        ),
    ],
)
def test_matcher_to_dict_round_trip(matcher: m.BaseMatcherNode, node: cst.CSTNode) -> None:
    config = _matcher_to_dict(matcher)
    parsed_matcher = _parse_matcher(config)

    assert m.matches(node, parsed_matcher)
    assert m.matches(node, matcher)
