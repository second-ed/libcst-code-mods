from __future__ import annotations

import attrs
import libcst as cst
import libcst.matchers as m

from libcst_code_mods.core.base_cst_transformer import BaseCstTransformer


@attrs.define
class ReorderParams(BaseCstTransformer):
    fn_name: str
    new_order: list[str]

    def visit_FunctionDef(self, node: cst.FunctionDef) -> None:  # noqa: N802
        if node.name.value == self.fn_name:
            self.param_order = [p.name.value for p in node.params.params]
            self.index_map = [self.param_order.index(name) for name in self.new_order]

    def leave_FunctionDef(self, original_node: cst.FunctionDef, updated_node: cst.FunctionDef) -> cst.FunctionDef:  # noqa: N802
        if original_node.name.value != self.fn_name:
            return updated_node

        return updated_node.with_changes(
            params=updated_node.params.with_changes(params=[updated_node.params.params[i] for i in self.index_map])
        )

    def leave_Call(self, original_node: cst.Call, updated_node: cst.Call) -> cst.Call:  # noqa: N802 ARG002
        if not m.matches(updated_node, m.Call(m.Name(self.fn_name))):
            return updated_node

        args = list(updated_node.args)

        if all(arg.keyword is None for arg in args):
            return updated_node.with_changes(args=[args[i] for i in self.index_map])

        kwargs = {
            arg.keyword.value if arg.keyword else self.new_order[self.index_map[i]]: arg.value
            for i, arg in enumerate(args)
        }
        new_args = [cst.Arg(value=kwargs[name], keyword=cst.Name(name)) for name in self.new_order]
        return updated_node.with_changes(args=new_args)
