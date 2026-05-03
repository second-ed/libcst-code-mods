import attrs
import libcst as cst

from libcst_code_mods.transformers._base import BaseAttrsTransformer


@attrs.define
class ConvertFunctionSignature(BaseAttrsTransformer):
    new_name: str
    positional_map: dict[int, str]
    param_map: dict[str, str]

    def on_leave(self, original_node: cst.CSTNode, updated_node: cst.CSTNode) -> cst.CSTNode:  # noqa: ARG002

        if not isinstance(updated_node, cst.Call):
            return updated_node

        new_args: list[cst.Arg] = []

        for i, arg in enumerate(updated_node.args):
            if arg.star or (arg.keyword and arg.keyword.value.startswith("**")):
                new_args.append(arg)
                continue

            if arg.keyword is None:
                current_param_name = self.positional_map.get(i, f"arg{i}")
                new_param_name = self.param_map.get(current_param_name, current_param_name)
                new_args.append(cst.Arg(value=arg.value, keyword=cst.Name(new_param_name)))
            else:
                kw = arg.keyword.value
                new_kw = self.param_map.get(kw, self.positional_map.get(i, kw))
                new_args.append(arg.with_changes(keyword=cst.Name(new_kw)))

        return updated_node.with_changes(func=cst.Name(self.new_name), args=new_args)
