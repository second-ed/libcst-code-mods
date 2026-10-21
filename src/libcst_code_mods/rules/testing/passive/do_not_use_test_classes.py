from collections.abc import Collection
from typing import ClassVar

import attrs
import libcst as cst

from libcst_code_mods.core.base_cst_visitor import BaseCstVisitor
from libcst_code_mods.core.refactoring_rule import RefactoringRule
from libcst_code_mods.rules._rule_mapping import RULE_NAME_MAPPING, register_rule, register_rule_visitor
from libcst_code_mods.rules.testing.passive._utils import in_test_file


@register_rule
@attrs.frozen
class DoNotUseTestClasses(RefactoringRule):
    pass


@register_rule_visitor(DoNotUseTestClasses)
@attrs.define
class DoNotUseTestClassesVisitor(BaseCstVisitor):
    METADATA_DEPENDENCIES: ClassVar[Collection[cst.metadata.ProviderT]] = (cst.metadata.PositionProvider,)

    def visit_ClassDef(self, node: cst.ClassDef) -> bool | None:  # noqa: N802
        if in_test_file(self.path) and node.name.value.startswith("Test"):
            self.add_diagnostic(node, RULE_NAME_MAPPING[self.__class__], "use a parametrized pytest function instead")
        return super().visit_ClassDef(node)
