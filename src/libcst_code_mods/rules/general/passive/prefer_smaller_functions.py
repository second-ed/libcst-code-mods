from collections.abc import Collection
from typing import ClassVar

import attrs
import libcst as cst
from attrs.validators import gt
from libcst.metadata import PositionProvider

from libcst_code_mods.core.base_cst_visitor import BaseCstVisitor
from libcst_code_mods.core.refactoring_rule import RefactoringRule
from libcst_code_mods.rules._rule_mapping import RULE_NAME_MAPPING, register_rule, register_rule_visitor


@register_rule
@attrs.define(frozen=True)
class PreferSmallerFunctions(RefactoringRule):
    statement_limit: int = attrs.field(default=6, validator=gt(0))
    allowed_functions: list[str] = attrs.field(factory=list)


@register_rule_visitor(PreferSmallerFunctions)
@attrs.define
class PreferSmallerFunctionsVisitor(BaseCstVisitor):
    METADATA_DEPENDENCIES: ClassVar[Collection[cst.metadata.ProviderT]] = (PositionProvider,)

    statement_limit: int
    allowed_functions: list[str]

    def visit_FunctionDef(self, node: cst.FunctionDef) -> bool | None:  # noqa: N802
        if node.name.value not in self.allowed_functions and (n_stmts := len(node.body.body)) > self.statement_limit:
            self.add_diagnostic(
                node,
                RULE_NAME_MAPPING[self.__class__],
                f"Prefer smaller focused pure functions with no more than {self.statement_limit} statements. `{node.name.value}` has {n_stmts}.",
            )

        return super().visit_FunctionDef(node)
