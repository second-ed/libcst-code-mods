import attrs
import libcst as cst
import libcst.matchers as m

from libcst_code_mods.core.base_cst_transformer import BaseCstTransformer
from libcst_code_mods.core.base_cst_visitor import BaseCstVisitor
from libcst_code_mods.core.refactoring_rule import RefactoringRule
from libcst_code_mods.rules._cst_utils import normalise
from libcst_code_mods.rules._rule_mapping import register_rule_transformer, register_rule_visitor


@attrs.define(frozen=True)
class RemoveKwargsIfDefaultValue(RefactoringRule):
    fn_name: str


@register_rule_visitor(RemoveKwargsIfDefaultValue)
@attrs.define
class RemoveKwargsIfDefaultValueVisitor(BaseCstVisitor):
    fn_name: str

    def visit_FunctionDef(self, node: cst.FunctionDef) -> None:  # noqa: N802
        if m.matches(node.name, m.Name(self.fn_name)):
            self.context.data["default_params"] = {
                p.name.value: p.default for p in node.params.params if p.default is not None
            }


@register_rule_transformer(RemoveKwargsIfDefaultValue)
@attrs.define
class RemoveKwargsIfDefaultValueTransformer(BaseCstTransformer):
    fn_name: str
    default_params: dict[str, cst.BaseExpression]

    def leave_Call(self, original_node: cst.Call, updated_node: cst.Call) -> cst.Call:  # noqa: N802 ARG002
        if not m.matches(updated_node, m.Call(m.Name(self.fn_name))):
            return updated_node

        new_args = []

        for arg in updated_node.args:
            if arg.keyword is None:
                new_args.append(arg)
                continue

            default = self.default_params.get(arg.keyword.value)

            if default is None:
                new_args.append(arg)
                continue

            if normalise(default) != normalise(arg.value):
                new_args.append(arg)

        return updated_node.with_changes(args=new_args)
