from __future__ import annotations

import attrs
import libcst as cst
import libcst.matchers as m

from libcst_code_mods.transformers._base import BaseAttrsTransformer


@attrs.define
class ReplaceTypeHint(BaseAttrsTransformer):
    old: str
    new: str

    def leave_Param(self, original_node: cst.Param, updated_node: cst.Param) -> cst.Param:  # noqa: N802 ARG002
        if self.matcher is not None and not m.matches(updated_node, self.matcher):
            return updated_node

        if updated_node.annotation and m.matches(updated_node.annotation.annotation, m.Name(self.old)):
            return updated_node.with_changes(annotation=cst.Annotation(cst.Name(self.new)))
        return updated_node
