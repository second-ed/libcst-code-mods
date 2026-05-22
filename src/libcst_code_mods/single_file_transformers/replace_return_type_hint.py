from __future__ import annotations

import attrs
import libcst as cst
import libcst.matchers as m

from libcst_code_mods.core.base_cst_transformer import BaseCstTransformer


@attrs.define
class ReplaceReturnTypeHint(BaseCstTransformer):
    old: str
    new: str
    function_name: str | None = None

    def leave_FunctionDef(self, original_node: cst.FunctionDef, updated_node: cst.FunctionDef) -> cst.FunctionDef:  # noqa: N802 ARG002
        if self.function_name is not None and not m.matches(updated_node.name, m.Name(self.function_name)):
            return updated_node

        if updated_node.returns and m.matches(updated_node.returns.annotation, m.Name(self.old)):
            return updated_node.with_changes(returns=cst.Annotation(annotation=cst.Name(self.new)))
        return updated_node
