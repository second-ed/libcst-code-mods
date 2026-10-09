from collections.abc import Collection, Generator, Sequence
from itertools import groupby
from operator import itemgetter
from pathlib import Path
from typing import ClassVar

import attrs
import libcst as cst
import libcst.matchers as m
from libcst.metadata import CodeRange, PositionProvider

from libcst_code_mods.core.base_cst_transformer import BaseCstTransformer
from libcst_code_mods.core.base_cst_visitor import BaseCstVisitor
from libcst_code_mods.core.diagnostics import Diagnostic, relative_path
from libcst_code_mods.core.refactoring_rule import RefactoringRule
from libcst_code_mods.rules._cst_utils import normalise
from libcst_code_mods.rules._rule_mapping import (
    RULE_NAME_MAPPING,
    register_rule,
    register_rule_transformer,
    register_rule_visitor,
)
from libcst_code_mods.rules.testing.passive._utils import in_test

MIN_ASSERTION_GROUP_SIZE = 2


@register_rule
@attrs.define(frozen=True)
class AssertAgainstFullObject(RefactoringRule):
    pass


@register_rule_visitor(AssertAgainstFullObject)
@attrs.define
class AssertAgainstFullObjectVisitor(BaseCstVisitor):
    METADATA_DEPENDENCIES: ClassVar[Collection[cst.metadata.ProviderT]] = (PositionProvider,)

    def visit_FunctionDef(self, node: cst.FunctionDef) -> bool | None:  # noqa: N802
        if in_test(self.path, node):
            for statements in _assertion_groups(node.body.body):
                self._report(statements)
        return super().visit_FunctionDef(node)

    def _report(self, statements: tuple[cst.BaseStatement | cst.BaseSmallStatement, ...]) -> None:
        first_position = self.get_metadata(PositionProvider, statements[0].body[0])
        last_position = self.get_metadata(PositionProvider, statements[-1].body[0])
        self.context.paths.add(self.path)
        self.context.diagnostics.add(
            Diagnostic(
                rule=RULE_NAME_MAPPING[self.__class__],
                path=relative_path(Path(self.path), self.context.root),
                code_range=CodeRange(start=first_position.start, end=last_position.end),
                code="".join(normalise(statement) for statement in statements),
                instead="Assert against the entire object, not one of its attributes or subscripts.",
            )
        )


@register_rule_transformer(AssertAgainstFullObject)
@attrs.define
class AssertAgainstFullObjectTransformer(BaseCstTransformer):
    pass


def _assertion_groups(
    statements: Sequence[cst.BaseStatement] | Sequence[cst.BaseSmallStatement],
) -> Generator[tuple[cst.BaseStatement | cst.BaseSmallStatement, ...], None, None]:
    keyed_statements = ((statement, _asserted_object(statement)) for statement in statements)
    for object_name, group in groupby(keyed_statements, key=itemgetter(1)):
        if object_name is None:
            continue
        statements_for_object = tuple(statement for statement, _ in group)
        if len(statements_for_object) >= MIN_ASSERTION_GROUP_SIZE:
            yield statements_for_object


def _asserted_object(statement: cst.BaseStatement) -> str | None:
    if (
        matched := m.extract(
            statement, m.SimpleStatementLine(body=[m.Assert(test=m.SaveMatchedNode(m.DoNotCare(), "test"))])
        )
    ) is None:
        return None

    test = matched["test"]
    expressions = (
        (test.left, *(comparison.comparator for comparison in test.comparisons))
        if m.matches(test, m.Comparison())
        else (test,)
    )

    for expression in expressions:
        if (base := _attribute_or_subscript_base(expression)) is not None:
            return normalise(base)
    return None


def _attribute_or_subscript_base(expression: cst.BaseExpression) -> cst.BaseExpression | None:
    if not m.matches(expression, m.OneOf(m.Attribute(), m.Subscript())):
        return None

    base = expression.value
    while m.matches(base, m.OneOf(m.Attribute(), m.Subscript())):
        base = base.value
    return base
