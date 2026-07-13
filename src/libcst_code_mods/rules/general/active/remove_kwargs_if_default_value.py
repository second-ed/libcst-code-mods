import attrs
import libcst as cst

from libcst_code_mods.core.base_cst_transformer import BaseCstTransformer
from libcst_code_mods.core.base_cst_visitor import BaseCstVisitor
from libcst_code_mods.core.refactoring_rule import RefactoringRule
from libcst_code_mods.rules._cst_utils import normalise
from libcst_code_mods.rules._rule_mapping import register_rule, register_rule_transformer, register_rule_visitor


@register_rule
@attrs.define(frozen=True)
class RemoveKwargsIfDefaultValue(RefactoringRule):
    """Examples:

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def main() -> None:
                func(0, "a", 2.0)
                func(2, c=0.0, b="b")
                func(a=4, b="c", c=4.0)

        Post-transformer:

        .. code-block:: python

            def main() -> None:
                func(0, "a", 2.0)
                func(2)
                func(a=4, b="c", c=4.0)
    ---
    """

    fn_names: list[str]


@register_rule_visitor(RemoveKwargsIfDefaultValue)
@attrs.define
class RemoveKwargsIfDefaultValueVisitor(BaseCstVisitor):
    fn_names: list[str]

    def visit_FunctionDef(self, node: cst.FunctionDef) -> None:  # noqa: N802
        if node.name.value in self.fn_names:
            self.context.data.setdefault("default_params", {})[node.name.value] = {
                p.name.value: p.default for p in node.params.params if p.default is not None
            }
            self.context.paths.add(self.path)

    def visit_Call(self, node: cst.Call) -> None:  # noqa: N802
        if node.func.value in self.fn_names:
            self.context.paths.add(self.path)


@register_rule_transformer(RemoveKwargsIfDefaultValue)
@attrs.define
class RemoveKwargsIfDefaultValueTransformer(BaseCstTransformer):
    fn_names: list[str]
    default_params: dict[str, cst.BaseExpression]

    def leave_Call(self, original_node: cst.Call, updated_node: cst.Call) -> cst.Call:  # noqa: N802 ARG002
        if updated_node.func.value not in self.fn_names:
            return updated_node

        fn_args = self.default_params[updated_node.func.value]

        new_args = []

        for arg in updated_node.args:
            if arg.keyword is None:
                new_args.append(arg)
                continue

            default = fn_args.get(arg.keyword.value)

            if default is None:
                new_args.append(arg)
                continue

            if normalise(default) != normalise(arg.value):
                new_args.append(arg)

        return updated_node.with_changes(args=new_args)
