from collections.abc import Collection
from typing import ClassVar

import attrs
import libcst as cst
import libcst.matchers as m
from attrs.validators import gt
from libcst.metadata import PositionProvider

from libcst_code_mods.core.base_cst_visitor import BaseCstVisitor
from libcst_code_mods.core.refactoring_rule import RefactoringRule
from libcst_code_mods.rules._rule_mapping import RULE_NAME_MAPPING, register_rule, register_rule_visitor


@register_rule
@attrs.frozen
class PreferSimplerFunctions(RefactoringRule):
    branch_limit: int = attrs.field(default=6, validator=gt(0))
    allowed_functions: list[str] = attrs.field(factory=list)


DECISIONS = m.OneOf(m.If(), m.Else(), m.For(), m.While(), m.IfExp(), m.ExceptHandler(), m.MatchCase(), m.And(), m.Or())


@register_rule_visitor(PreferSimplerFunctions)
@attrs.define
class PreferSimplerFunctionsVisitor(BaseCstVisitor):
    METADATA_DEPENDENCIES: ClassVar[Collection[cst.metadata.ProviderT]] = (PositionProvider,)

    branch_limit: int
    allowed_functions: list[str]

    def visit_FunctionDef(self, node: cst.FunctionDef) -> bool | None:  # noqa: N802
        if (
            node.name.value not in self.allowed_functions
            and (n_branches := len(m.findall(node, DECISIONS))) > self.branch_limit
        ):
            self.add_diagnostic(
                node,
                RULE_NAME_MAPPING[self.__class__],
                f"Prefer simpler focused pure functions with no more than {self.branch_limit} branches. `{node.name.value}` has {n_branches}.",
            )

        return super().visit_FunctionDef(node)
