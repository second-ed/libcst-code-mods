import attrs
import libcst as cst

from libcst_code_mods.core.base_cst_transformer import BaseCstTransformer
from libcst_code_mods.core.base_cst_visitor import BaseCstVisitor
from libcst_code_mods.core.refactoring_rule import RefactoringRule
from libcst_code_mods.rules._rule_mapping import register_rule_transformer, register_rule_visitor


@attrs.define(frozen=True)
class AddKwargs(RefactoringRule):
    fn_names: list[str]


@register_rule_visitor(AddKwargs)
@attrs.define
class AddKwargsVisitor(BaseCstVisitor):
    fn_names: list[str]

    def visit_FunctionDef(self, node: cst.FunctionDef) -> None:  # noqa: N802
        if node.name.value in self.fn_names:
            param_names = [p.name.value for p in node.params.params]

            self.context.data.setdefault("param_names", {})[node.name.value] = param_names
            self.context.paths.add(self.path)

    def visit_Call(self, node: cst.Call) -> bool | None:  # noqa: N802
        if node.func.value in self.fn_names:
            self.context.paths.add(self.path)
        return super().visit_Call(node)


@register_rule_transformer(AddKwargs)
@attrs.define
class AddKwargsTransformer(BaseCstTransformer):
    fn_names: list[str]
    param_names: dict[str, list[str]]

    def leave_Call(self, original_node: cst.Call, updated_node: cst.Call) -> cst.Call:  # noqa: N802 ARG002
        if updated_node.func.value not in self.fn_names:
            return updated_node

        args = list(updated_node.args)
        fn_kwarg_list = self.param_names[updated_node.func.value]

        kwargs = {arg.keyword.value if arg.keyword else fn_kwarg_list[i]: arg.value for i, arg in enumerate(args)}
        new_args = [cst.Arg(value=kwargs[name], keyword=cst.Name(name)) for name in fn_kwarg_list]
        return updated_node.with_changes(args=new_args)
