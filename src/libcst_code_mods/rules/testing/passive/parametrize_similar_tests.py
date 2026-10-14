from __future__ import annotations

from collections.abc import Iterable
from functools import partial
from itertools import takewhile

import attrs
import libcst as cst
import libcst.matchers as m

from libcst_code_mods.core.base_cst_transformer import BaseCstTransformer
from libcst_code_mods.core.base_cst_visitor import BaseCstVisitor
from libcst_code_mods.core.refactoring_rule import RefactoringRule
from libcst_code_mods.rules._cst_utils import normalise
from libcst_code_mods.rules._rule_mapping import register_rule, register_rule_transformer, register_rule_visitor

MIN_SIMILAR_TESTS = 2
MIN_COMMON_NAME_PARTS = 2

ASSIGNMENT = m.SimpleStatementLine(
    body=[
        m.Assign(
            targets=[m.AssignTarget(target=m.SaveMatchedNode(m.Name(), "name"))],
            value=m.SaveMatchedNode(m.DoNotCare(), "value"),
        )
    ]
)
ASSERTION = m.SimpleStatementLine(
    body=[
        m.Assert(
            test=m.Comparison(
                left=m.SaveMatchedNode(m.DoNotCare(), "left"),
                comparisons=[
                    m.ComparisonTarget(operator=m.Equal(), comparator=m.SaveMatchedNode(m.DoNotCare(), "expected"))
                ],
            )
        )
    ]
)
IMPORT_STATEMENT = m.SimpleStatementLine(body=[m.OneOf(m.Import(), m.ImportFrom())])


@register_rule
@attrs.define(frozen=True)
class ParametrizeSimilarTests(RefactoringRule):
    pass


@register_rule_visitor(ParametrizeSimilarTests)
@attrs.define
class ParametrizeSimilarTestsVisitor(BaseCstVisitor):
    def visit_Module(self, node: cst.Module) -> bool | None:  # noqa: N802
        functions = [statement for statement in node.body if isinstance(statement, cst.FunctionDef)]
        candidates = [candidate for candidate in map(_candidate, functions) if candidate is not None]

        for group in _similar_groups(candidates):
            replacement = _replacement(group)
            self.context.data.setdefault("replacements", []).append(replacement)
            self.context.paths.add(self.path)

        return super().visit_Module(node)


@register_rule_transformer(ParametrizeSimilarTests)
@attrs.define
class ParametrizeSimilarTestsTransformer(BaseCstTransformer):
    replacements: list[_Replacement]

    def leave_Module(self, _original_node: cst.Module, updated_node: cst.Module) -> cst.Module:  # noqa: N802
        if not self.replacements:
            return updated_node

        replacement_by_name = {
            source_name: replacement for replacement in self.replacements for source_name in replacement.source_names
        }
        body = []
        changed = False
        inserted: set[str] = set()
        for statement in updated_node.body:
            if not isinstance(statement, cst.FunctionDef) or statement.name.value not in replacement_by_name:
                body.append(statement)
                continue
            replacement = replacement_by_name[statement.name.value]
            if replacement.name not in inserted:
                body.append(cst.parse_statement(replacement.code))
                inserted.add(replacement.name)
            changed = True

        if not changed:
            return updated_node
        body = _insert_pytest_import_if_missing(body)
        return updated_node.with_changes(body=body)


@attrs.define(frozen=True)
class _TestCandidate:
    function: cst.FunctionDef
    name: str
    param_names: tuple[str, ...]
    param_values: tuple[str, ...]
    assertion_left: str
    expected_value: str
    assertion_message: str | None


@attrs.define(frozen=True)
class _Replacement:
    name: str
    source_names: tuple[str, ...]
    code: str


def _candidate(function: cst.FunctionDef) -> _TestCandidate | None:
    if not function.name.value.startswith("test_") or not isinstance(function.body, cst.IndentedBlock):
        return None

    param_names, param_values, assertions = [], [], []

    for statement in function.body.body:
        if (extracted := m.extract(statement, ASSIGNMENT)) is not None:
            param_names.append(extracted["name"].value)
            param_values.append(normalise(extracted["value"]))
        if m.matches(statement, ASSERTION):
            assertions.append(statement.body[0])

    if (
        not param_names
        or not param_values
        or len(assertions) != 1
        or len(param_names) + len(assertions) != len(function.body.body)
    ):
        return None

    assertion = assertions[0]
    return _TestCandidate(
        function=function,
        name=function.name.value,
        param_names=tuple(param_names),
        param_values=tuple(param_values),
        assertion_left=normalise(assertion.test.left),
        expected_value=normalise(assertion.test.comparisons[0].comparator),
        assertion_message=normalise(assertion.msg) if assertion.msg is not None else None,
    )


def _similar_groups(candidates: Iterable[_TestCandidate]) -> Iterable[tuple[_TestCandidate, ...]]:
    grouped: dict[tuple[tuple[str, ...], str], list[_TestCandidate]] = {}
    for candidate in candidates:
        grouped.setdefault((candidate.param_names, candidate.assertion_left), []).append(candidate)
    return (tuple(group) for group in grouped.values() if len(group) >= MIN_SIMILAR_TESTS)


def _replacement(group: tuple[_TestCandidate, ...]) -> _Replacement:
    first = group[0]
    common_name = _common_test_name(candidate.name for candidate in group)
    param_names = (*first.param_names, "expected_result")
    has_assertion_message = any(candidate.assertion_message is not None for candidate in group)
    generated_param_names = (*param_names, "assert_msg") if has_assertion_message else param_names

    rows = map(partial(_create_pytest_param, has_assertion_message=has_assertion_message), group)

    return_annotation = f" -> {normalise(first.function.returns.annotation)}" if first.function.returns else ""
    code = (
        "@pytest.mark.parametrize(\n"
        f"    ({', '.join(repr(name) for name in generated_param_names)}),\n"
        f"    [{', '.join(rows)}],\n"
        ")\n"
        f"def {common_name}({', '.join(generated_param_names)}){return_annotation}:\n"
        f"    assert {first.assertion_left} == expected_result{', assert_msg' if has_assertion_message else ''}\n"
    )
    return _Replacement(name=common_name, source_names=tuple(candidate.name for candidate in group), code=code)


def _create_pytest_param(candidate: _TestCandidate, *, has_assertion_message: bool) -> str:
    params = ", ".join(
        (*candidate.param_values, candidate.expected_value, _assertion_message(candidate))
        if has_assertion_message
        else (*candidate.param_values, candidate.expected_value)
    )
    return f"pytest.param({params}, id={candidate.name.removeprefix('test_').replace('_', ' ')!r})"


def _common_test_name(names: Iterable[str]) -> str:
    if not (parts := [name.split("_") for name in names]):
        raise ValueError("names must contain at least one name")

    common = [column[0] for column in takewhile(lambda column: len(set(column)) == 1, zip(*parts, strict=False))]
    return "_".join(common) if len(common) >= MIN_COMMON_NAME_PARTS else parts[0][0]


def _assertion_message(candidate: _TestCandidate) -> str:
    if candidate.assertion_message is None:
        return '"no assertion message provided"'

    message = candidate.assertion_message
    for name, value in zip(candidate.param_names, candidate.param_values, strict=True):
        for pattern in (f"{{{name} = }}", f"{{{name}=}}", f"{{{name} =}}", f"{{{name}= }}"):
            message = message.replace(pattern, f"{name} = {value}")
    return message


def _has_pytest_import(body: Iterable[cst.BaseStatement]) -> bool:
    return bool(m.findall(cst.Module(body=tuple(body)), m.ImportAlias(name=m.Name("pytest"))))


def _insert_pytest_import_if_missing(body: list[cst.BaseStatement]) -> list[cst.BaseStatement]:
    if _has_pytest_import(body):
        return body
    import_index = next(
        (index for index, statement in enumerate(body) if not m.matches(statement, IMPORT_STATEMENT)), len(body)
    )
    body.insert(
        import_index,
        cst.SimpleStatementLine(
            body=[cst.Import(names=[cst.ImportAlias(name=cst.Name(value="pytest"))])], leading_lines=[cst.EmptyLine()]
        ),
    )
    return body
