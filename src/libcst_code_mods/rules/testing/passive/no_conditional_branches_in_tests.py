from collections.abc import Collection
from typing import ClassVar

import attrs
import libcst as cst
import libcst.matchers as m

from libcst_code_mods.core.base_cst_visitor import BaseCstVisitor
from libcst_code_mods.core.refactoring_rule import RefactoringRule
from libcst_code_mods.rules._rule_mapping import RULE_NAME_MAPPING, register_rule, register_rule_visitor
from libcst_code_mods.rules.testing.passive._utils import in_test_file


@register_rule
@attrs.frozen
class NoConditionalBranchesInTests(RefactoringRule):
    pass


TEST_FUNCTION_MATCHER = m.FunctionDef(
    name=m.Name(value=m.MatchIfTrue(lambda value: value.startswith("test_"))),
    body=m.SaveMatchedNode(m.DoNotCare(), "test_body"),
)
IF_WITH_ELIF_MATCHER = m.If(orelse=m.SaveMatchedNode(m.If(), "elif"))


@register_rule_visitor(NoConditionalBranchesInTests)
@attrs.define
class NoConditionalBranchesInTestsVisitor(BaseCstVisitor):
    METADATA_DEPENDENCIES: ClassVar[Collection[cst.metadata.ProviderT]] = (cst.metadata.PositionProvider,)
    _test_if_nodes: set[int] = attrs.field(factory=set)
    _elif_nodes: set[int] = attrs.field(factory=set)

    def visit_FunctionDef(self, node: cst.FunctionDef) -> bool | None:  # noqa: N802
        if in_test_file(self.path) and (matched := m.extract(node, TEST_FUNCTION_MATCHER)) is not None:
            self._test_if_nodes.update(id(if_node) for if_node in m.findall(matched["test_body"], m.If()))
        return super().visit_FunctionDef(node)

    def visit_If(self, node: cst.If) -> bool | None:  # noqa: N802
        if id(node) in self._test_if_nodes and id(node) not in self._elif_nodes:
            self.add_diagnostic(
                node,
                RULE_NAME_MAPPING[self.__class__],
                "Replace the conditional with separate test cases or parametrized inputs so each behavior is tested directly.",
            )
            self._mark_elif_nodes(node)
        return super().visit_If(node)

    def _mark_elif_nodes(self, node: cst.If) -> None:
        matched = m.extract(node, IF_WITH_ELIF_MATCHER)
        while matched is not None:
            elif_node = matched["elif"]
            self._elif_nodes.add(id(elif_node))
            matched = m.extract(elif_node, IF_WITH_ELIF_MATCHER)
