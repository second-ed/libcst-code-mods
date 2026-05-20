from __future__ import annotations

import attrs
import libcst as cst
import libcst.matchers as m

from libcst_code_mods.transformers._base import BaseAttrsTransformer


@attrs.define
class ReplaceReturnTypeHint(BaseAttrsTransformer):
    old: str
    new: str
    function_name: str | None = None
    _current_function: str | None = attrs.field(init=False, default=None)

    def visit_FunctionDef(self, node: cst.FunctionDef) -> None:  # noqa: N802
        self._current_function = node.name.value

    def leave_FunctionDef(self, original_node: cst.FunctionDef, updated_node: cst.FunctionDef) -> cst.FunctionDef:  # noqa: N802 ARG002
        if self.function_name is not None and self._current_function != self.function_name:
            return updated_node

        if self.matcher is not None and not m.matches(updated_node, self.matcher):
            return updated_node

        if updated_node.returns and m.matches(updated_node.returns.annotation, m.Name(self.old)):
            return updated_node.with_changes(returns=cst.Annotation(annotation=cst.Name(self.new)))
        return updated_node
