from __future__ import annotations

import attrs
import libcst as cst
import libcst.matchers as m

from libcst_code_mods.transformers._base import BaseAttrsTransformer


@attrs.define
class ReplaceParamTypeHint(BaseAttrsTransformer):
    old: str
    new: str
    function_name: str | None = None
    _current_function: str | None = attrs.field(init=False, default=None)

    def visit_FunctionDef(self, node: cst.FunctionDef) -> None:  # noqa: N802
        self._current_function = node.name.value

    def leave_FunctionDef(self, original_node: cst.FunctionDef, updated_node: cst.FunctionDef) -> cst.FunctionDef:  # noqa: N802 ARG002
        self._current_function = None
        return updated_node

    def leave_Param(self, original_node: cst.Param, updated_node: cst.Param) -> cst.Param:  # noqa: N802 ARG002
        if self.function_name is not None and self._current_function != self.function_name:
            return updated_node

        if self.matcher is not None and not m.matches(updated_node, self.matcher):
            return updated_node

        if updated_node.annotation and m.matches(updated_node.annotation.annotation, m.Name(self.old)):
            return updated_node.with_changes(annotation=cst.Annotation(cst.Name(self.new)))
        return updated_node
