"""repo-map-desc: Rename all variables of a certain type with the same name, this is useful for custom objects that there will only be 1 instances of at a time.

Modifies on three cases:
1. an assignment with a type hint
2. a parameter with a type hint
3. a name that has been previously updated by 1. or 2.
"""

from __future__ import annotations

import attrs
import libcst as cst
import libcst.matchers as m

import libcst_code_mods.matchers as mat
from libcst_code_mods.transformers._base import BaseMetadataTransformer


@attrs.define
class RenameVariableOfType(BaseMetadataTransformer):
    type_hint: str
    new_variable_name: str
    replaced_names: list[str] = attrs.field(factory=list)

    def on_leave(self, original_node: cst.CSTNode, updated_node: cst.CSTNode) -> cst.CSTNode:  # noqa: ARG002
        if m.matches(updated_node, mat.assignment_has_type_hint(m.Name(self.type_hint))):
            self.replaced_names.append(updated_node.target.value)
            return updated_node.with_changes(target=cst.Name(self.new_variable_name))

        if m.matches(updated_node, mat.param_has_type_hint(m.Name(self.type_hint))):
            self.replaced_names.append(updated_node.name.value)
            return updated_node.with_changes(name=cst.Name(self.new_variable_name))

        if m.matches(updated_node, m.Name()) and updated_node.value in self.replaced_names:
            return updated_node.with_changes(value=self.new_variable_name)

        return updated_node
