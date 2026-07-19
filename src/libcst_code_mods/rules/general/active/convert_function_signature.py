import attrs
import libcst as cst
import libcst.matchers as m

from libcst_code_mods.core.base_cst_transformer import BaseCstTransformer
from libcst_code_mods.core.base_cst_visitor import BaseCstVisitor
from libcst_code_mods.core.refactoring_rule import RefactoringRule
from libcst_code_mods.rules._rule_mapping import register_rule, register_rule_transformer, register_rule_visitor


@register_rule
@attrs.define(frozen=True)
class ConvertFunctionSignature(RefactoringRule):
    """Examples:

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def main():
                x = add(1, 2)
                y = add(2, b=2)
                print(y)
                return x + y + add(a=-1, b=-1)

        Post-transformer:

        .. code-block:: python

            def main():
                x = new_sum(value_1=1, value_2=2)
                y = new_sum(value_1=2, value_2=2)
                print(y)
                return x + y + new_sum(value_1=-1, value_2=-1)
    ---
    """

    fn_name: str
    new_name: str
    param_map: dict[str, str]


@register_rule_visitor(ConvertFunctionSignature)
@attrs.define
class ConvertFunctionSignatureVisitor(BaseCstVisitor):
    fn_name: str

    def visit_FunctionDef(self, node: cst.FunctionDef) -> None:  # noqa: N802
        if not m.matches(node, m.FunctionDef(m.Name(self.fn_name))):
            return

        positional_map: dict[int, str] = {i: param.name.value for i, param in enumerate(node.params.params)}
        self.context.data["positional_map"] = positional_map
        self.context.paths.add(self.path)

    def visit_Call(self, node: cst.Call) -> bool | None:  # noqa: N802

        if not m.matches(
            node,
            m.Call(func=m.OneOf(m.Name(self.fn_name), m.Attribute(value=m.DoNotCare(), attr=m.Name(self.fn_name)))),
        ):
            return None
        self.context.paths.add(self.path)
        return super().visit_Call(node)


@register_rule_transformer(ConvertFunctionSignature)
@attrs.define
class ConvertFunctionSignatureTransformer(BaseCstTransformer):
    fn_name: str
    new_name: str
    positional_map: dict[int, str]
    param_map: dict[str, str]

    def leave_Call(self, original_node: cst.Call, updated_node: cst.Call) -> cst.Call:  # noqa: N802
        if not m.matches(
            original_node,
            m.Call(func=m.OneOf(m.Name(self.fn_name), m.Attribute(value=m.DoNotCare(), attr=m.Name(self.fn_name)))),
        ):
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
                continue
            kw = arg.keyword.value
            new_kw = self.param_map.get(kw, self.positional_map.get(i, kw))
            new_args.append(arg.with_changes(keyword=cst.Name(new_kw)))

        return updated_node.with_changes(func=cst.Name(self.new_name), args=new_args)
