from collections.abc import Collection
from typing import ClassVar

import attrs
import libcst as cst

from libcst_code_mods.core.base_cst_transformer import BaseCstTransformer
from libcst_code_mods.core.base_cst_visitor import BaseCstVisitor
from libcst_code_mods.core.refactoring_rule import RefactoringRule
from libcst_code_mods.rules._rule_mapping import (
    RULE_NAME_MAPPING,
    register_rule,
    register_rule_transformer,
    register_rule_visitor,
)


@register_rule
@attrs.define(frozen=True)
class DoNotUseUnittest(RefactoringRule):
    pass


@register_rule_visitor(DoNotUseUnittest)
@attrs.define
class DoNotUseUnittestVisitor(BaseCstVisitor):
    METADATA_DEPENDENCIES: ClassVar[Collection[cst.metadata.ProviderT]] = (cst.metadata.PositionProvider,)

    def visit_Import(self, node: cst.Import) -> bool | None:  # noqa: N802
        if any(_starts_with_unittest(alias.name) for alias in node.names):
            self._add_diagnostic(node)
        return super().visit_Import(node)

    def visit_ImportFrom(self, node: cst.ImportFrom) -> bool | None:  # noqa: N802
        if node.module is not None and _starts_with_unittest(node.module):
            self._add_diagnostic(node)
        return super().visit_ImportFrom(node)

    def _add_diagnostic(self, node: cst.Import | cst.ImportFrom) -> None:
        self.add_diagnostic(node, RULE_NAME_MAPPING[self.__class__], "Use pytest instead of unittest")


def _starts_with_unittest(node: cst.BaseExpression) -> bool:
    name = cst.helpers.get_full_name_for_node(node)
    return name is not None and (name == "unittest" or name.startswith("unittest."))


@register_rule_transformer(DoNotUseUnittest)
@attrs.define
class DoNotUseUnittestTransformer(BaseCstTransformer):
    pass
