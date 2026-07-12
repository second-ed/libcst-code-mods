import attrs
import libcst as cst
import libcst.matchers as m

from libcst_code_mods.core.base_cst_transformer import BaseCstTransformer
from libcst_code_mods.core.base_cst_visitor import BaseCstVisitor
from libcst_code_mods.core.refactoring_rule import RefactoringRule
from libcst_code_mods.rules._rule_mapping import register_rule, register_rule_transformer, register_rule_visitor


@register_rule
@attrs.define(frozen=True)
class ReorderParams(RefactoringRule):
    """Examples:

        Case:

        Pre-transformer:

        .. code-block:: python

            def main() -> None:
                func(0, "a", 2.0)
                func(2, c=3.0, b="b")
                func(a=4, b="c", c=4.0)

        Post-transformer:

        .. code-block:: python

            def main() -> None:
                func(2.0, "a", 0)
                func(c=3.0, b="b", a=2)
                func(c=4.0, b="c", a=4)


        Case:

        Pre-transformer:

        .. code-block:: python

            def func(a: int, b: str, c: float) -> str:
                if a % 2 == 0:
                    return b + str(c)
                return str(c)

        Post-transformer:

        .. code-block:: python

            def func(c: float, b: str, a: int) -> str:
                if a % 2 == 0:
                    return b + str(c)
                return str(c)
    ::
    """

    fn_name: str
    new_order: list[str]


@register_rule_visitor(ReorderParams)
@attrs.define
class ReorderParamsVisitor(BaseCstVisitor):
    fn_name: str
    new_order: list[str]

    def visit_FunctionDef(self, node: cst.FunctionDef) -> None:  # noqa: N802
        if m.matches(node.name, m.Name(self.fn_name)):
            param_order = [p.name.value for p in node.params.params]

            if not set(param_order) == set(self.new_order):
                raise ValueError(
                    f"new_order does not have all of the parameters to be able to reorder {self.new_order = } {param_order = }"
                )
            self.context.data["index_map"] = [param_order.index(name) for name in self.new_order]
            self.context.paths.add(self.path)


@register_rule_transformer(ReorderParams)
@attrs.define
class ReorderParamsTransformer(BaseCstTransformer):
    fn_name: str
    new_order: list[str]
    index_map: list[int]

    def leave_FunctionDef(self, original_node: cst.FunctionDef, updated_node: cst.FunctionDef) -> cst.FunctionDef:  # noqa: ARG002 N802
        if not m.matches(updated_node.name, m.Name(self.fn_name)):
            return updated_node

        param_map = {param.name.value: param for param in updated_node.params.params}

        return updated_node.with_changes(
            params=updated_node.params.with_changes(params=[param_map[name] for name in self.new_order])
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
