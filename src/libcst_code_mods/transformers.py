from __future__ import annotations

import attrs
import libcst as cst
import libcst.matchers as m

import libcst_code_mods.matchers as mat


@attrs.define
class RenameVariableOfType(cst.CSTTransformer):
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
