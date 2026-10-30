from collections.abc import Collection
from typing import ClassVar

import attrs
import libcst as cst
import libcst.matchers as m
from libcst.metadata import PositionProvider

from libcst_code_mods.core.base_cst_visitor import BaseCstVisitor
from libcst_code_mods.core.refactoring_rule import RefactoringRule
from libcst_code_mods.rules._rule_mapping import RULE_NAME_MAPPING, register_rule, register_rule_visitor


@register_rule
@attrs.define(frozen=True)
class DoNotUseStaticmethod(RefactoringRule):
    pass


@register_rule_visitor(DoNotUseStaticmethod)
@attrs.define
class DoNotUseStaticmethodVisitor(BaseCstVisitor):
    METADATA_DEPENDENCIES: ClassVar[Collection[cst.metadata.ProviderT]] = (PositionProvider,)

    def visit_FunctionDef(self, node: cst.FunctionDef) -> bool | None:  # noqa: N802
        if m.matches(node, m.FunctionDef(decorators=[m.Decorator(m.Name("staticmethod"))])):
            self.add_diagnostic(
                node,
                RULE_NAME_MAPPING[self.__class__],
                "use a free floating function if the method doesn't need to be attached to the object",
            )

        return super().visit_FunctionDef(node)
