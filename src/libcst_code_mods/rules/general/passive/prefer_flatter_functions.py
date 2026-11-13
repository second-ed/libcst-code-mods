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
@attrs.frozen
class PreferFlatterFunctions(RefactoringRule):
    indent_limit: int = attrs.field(default=3, validator=gt(0))
    allowed_functions: list[str] = attrs.field(factory=list)


@register_rule_visitor(PreferFlatterFunctions)
@attrs.define
class PreferFlatterFunctionsVisitor(BaseCstVisitor):
    METADATA_DEPENDENCIES: ClassVar[Collection[cst.metadata.ProviderT]] = (PositionProvider,)

    indent_limit: int
    allowed_functions: list[str]

    def visit_FunctionDef(self, node: cst.FunctionDef) -> bool | None:  # noqa: N802
        if node.name.value in self.allowed_functions:
            return super().visit_FunctionDef(node)

        counter = _MaxIndentationVisitor()
        node.body.visit(counter)

        if counter.max_depth > self.indent_limit:
            self.add_diagnostic(
                node,
                RULE_NAME_MAPPING[self.__class__],
                f"Prefer simpler focused pure functions with no more than {self.indent_limit} nested indents. `{node.name.value}` has {counter.max_depth}.",
            )

        return super().visit_FunctionDef(node)


@attrs.define
class _MaxIndentationVisitor(cst.CSTVisitor):
    depth = -1
    max_depth = 0

    def visit_IndentedBlock(self, node: cst.IndentedBlock) -> bool:  # noqa: ARG002, N802
        self.depth += 1
        self.max_depth = max(self.max_depth, self.depth)
        return True

    def leave_IndentedBlock(self, original_node: cst.IndentedBlock) -> None:  # noqa: N802
        self.depth -= 1
        return super().leave_IndentedBlock(original_node)

    def visit_FunctionDef(self, node: cst.FunctionDef) -> bool:  # noqa: ARG002, N802
        # Do not count blocks inside nested functions.
        return False
