import attrs
import libcst as cst
import libcst.matchers as m

import libcst_code_mods.matchers as mat
from libcst_code_mods.core.base_cst_transformer import BaseCstTransformer


@attrs.define
class ConvertFunctionSignature(BaseCstTransformer):
    function_name: str
    new_name: str
    positional_map: dict[int, str]
    param_map: dict[str, str]

    def leave_Call(self, original_node: cst.Call, updated_node: cst.Call) -> cst.Call:  # noqa: N802 ARG002
        if not m.matches(updated_node, mat.is_call_with_name(m.Name(self.function_name))):
            return updated_node

        new_args: list[cst.Arg] = []

        for i, arg in enumerate(updated_node.args):
            if arg.star:
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
