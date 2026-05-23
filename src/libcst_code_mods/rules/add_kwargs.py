import attrs
import libcst as cst
import libcst.matchers as m

from libcst_code_mods.core.base_cst_transformer import BaseCstTransformer
from libcst_code_mods.core.base_cst_visitor import BaseCstVisitor
from libcst_code_mods.core.refactoring_rule import RefactoringRule
from libcst_code_mods.rules._rule_mapping import register_rule_transformer, register_rule_visitor


@attrs.define(frozen=True)
class AddKwargs(RefactoringRule):
    fn_name: str


@register_rule_visitor(AddKwargs)
@attrs.define
class AddKwargsVisitor(BaseCstVisitor):
    fn_name: str

    def visit_FunctionDef(self, node: cst.FunctionDef) -> None:  # noqa: N802
        if m.matches(node.name, m.Name(self.fn_name)):
            param_names = [p.name.value for p in node.params.params]

            self.context.data["param_names"] = param_names


@register_rule_transformer(AddKwargs)
@attrs.define
class AddKwargsTransformer(BaseCstTransformer):
    fn_name: str
    param_names: list[str]

    def leave_Call(self, original_node: cst.Call, updated_node: cst.Call) -> cst.Call:  # noqa: N802 ARG002
        if not m.matches(updated_node, m.Call(m.Name(self.fn_name))):
            return updated_node

        args = list(updated_node.args)

        kwargs = {arg.keyword.value if arg.keyword else self.param_names[i]: arg.value for i, arg in enumerate(args)}
        new_args = [cst.Arg(value=kwargs[name], keyword=cst.Name(name)) for name in self.param_names]
        return updated_node.with_changes(args=new_args)
