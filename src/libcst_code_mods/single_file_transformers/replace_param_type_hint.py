from __future__ import annotations

import attrs
import libcst as cst
import libcst.matchers as m

from libcst_code_mods.core.base_cst_transformer import BaseCstTransformer


@attrs.define
class ReplaceParamTypeHint(BaseCstTransformer):
    old: str
    new: str
    fn_name: str | None = None
    _curr_fn: str | None = attrs.field(init=False, default=None)

    def visit_FunctionDef(self, node: cst.FunctionDef) -> None:  # noqa: N802
        self._curr_fn = node.name.value

    def leave_FunctionDef(self, original_node: cst.FunctionDef, updated_node: cst.FunctionDef) -> cst.FunctionDef:  # noqa: N802 ARG002
        self._curr_fn = None
        return updated_node

    def leave_Param(self, original_node: cst.Param, updated_node: cst.Param) -> cst.Param:  # noqa: N802 ARG002
        if self.fn_name is not None and self._curr_fn != self.fn_name:
            return updated_node

        if updated_node.annotation and m.matches(updated_node.annotation.annotation, m.Name(self.old)):
            return updated_node.with_changes(annotation=cst.Annotation(cst.Name(self.new)))
        return updated_node
