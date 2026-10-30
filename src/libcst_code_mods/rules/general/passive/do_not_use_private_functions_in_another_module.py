from collections.abc import Collection
from typing import ClassVar

import attrs
import libcst as cst
from libcst.metadata import PositionProvider, QualifiedNameSource

from libcst_code_mods.core.base_cst_visitor import BaseCstVisitor
from libcst_code_mods.core.refactoring_rule import RefactoringRule
from libcst_code_mods.rules._rule_mapping import RULE_NAME_MAPPING, register_rule, register_rule_visitor


@register_rule
@attrs.define(frozen=True)
class DoNotUsePrivateFunctionsInAnotherModule(RefactoringRule):
    pass


@register_rule_visitor(DoNotUsePrivateFunctionsInAnotherModule)
@attrs.define
class DoNotUsePrivateFunctionsInAnotherModuleVisitor(BaseCstVisitor):
    METADATA_DEPENDENCIES: ClassVar[Collection[cst.metadata.ProviderT]] = (
        PositionProvider,
        cst.metadata.FullyQualifiedNameProvider,
    )

    def visit_Call(self, node: cst.Call) -> bool | None:  # noqa: N802
        qualified_names = self.get_metadata(cst.metadata.FullyQualifiedNameProvider, node.func, set())
        if any(
            qualified_name.source is QualifiedNameSource.IMPORT
            and qualified_name.name.rsplit(".", maxsplit=1)[-1].startswith("_")
            for qualified_name in qualified_names
        ):
            self.add_diagnostic(
                node,
                RULE_NAME_MAPPING[self.__class__],
                "Use an equivalent public function. If none exists, make this function public and update its references",
            )

        return super().visit_Call(node)
