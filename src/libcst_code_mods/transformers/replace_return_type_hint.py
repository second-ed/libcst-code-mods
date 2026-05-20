from __future__ import annotations

import attrs
import libcst as cst
import libcst.matchers as m

from libcst_code_mods.transformers._base import BaseAttrsTransformer


@attrs.define
class ReplaceReturnTypeHint(BaseAttrsTransformer):
    old: str
    new: str

    def leave_FunctionDef(self, original_node: cst.FunctionDef, updated_node: cst.FunctionDef) -> cst.FunctionDef:  # noqa: N802 ARG002
        if self.matcher is not None and not m.matches(updated_node, self.matcher):
            return updated_node

        if updated_node.returns and m.matches(updated_node.returns.annotation, m.Name(self.old)):
            return updated_node.with_changes(returns=cst.Annotation(annotation=cst.Name(self.new)))
        return updated_node
