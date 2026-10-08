from collections.abc import Collection
from pathlib import Path
from typing import ClassVar

import attrs
import libcst as cst
import libcst.matchers as m
from libcst.metadata import PositionProvider

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


@register_rule
@attrs.define(frozen=True)
class MethodDoesNotUseSelf(RefactoringRule):
    pass


@register_rule_visitor(MethodDoesNotUseSelf)
@attrs.define
class MethodDoesNotUseSelfVisitor(BaseCstVisitor):
    METADATA_DEPENDENCIES: ClassVar[Collection[cst.metadata.ProviderT]] = (PositionProvider,)

    class_depth: int = 0
    function_depth: int = 0

    def visit_ClassDef(self, node: cst.ClassDef) -> bool:  # noqa: N802 ARG002
        self.class_depth += 1
        return True

    def leave_ClassDef(self, original_node: cst.ClassDef) -> None:  # noqa: N802 ARG002
        self.class_depth -= 1

    def visit_FunctionDef(self, node: cst.FunctionDef) -> bool:  # noqa: N802
        if (
            self.class_depth
            and not self.function_depth
            and _has_self_parameter(node)
            and not m.findall(node.body, m.Name("self"))
        ):
            self.context.paths.add(self.path)
            self.context.diagnostics.add(
                Diagnostic(
                    rule=RULE_NAME_MAPPING[self.__class__],
                    path=relative_path(Path(self.path), self.context.root),
                    code_range=self.get_metadata(PositionProvider, node),
                    code=normalise(node),
                    instead="use a free floating function if the method doesn't need to be attached to the object",
                )
            )

        self.function_depth += 1
        return True

    def leave_FunctionDef(self, original_node: cst.FunctionDef) -> None:  # noqa: N802 ARG002
        self.function_depth -= 1


@register_rule_transformer(MethodDoesNotUseSelf)
@attrs.define
class MethodDoesNotUseSelfTransformer(BaseCstTransformer):
    pass


def _has_self_parameter(node: cst.FunctionDef) -> bool:
    positional_parameters = (*node.params.posonly_params, *node.params.params)
    return bool(positional_parameters) and positional_parameters[0].name.value == "self"
