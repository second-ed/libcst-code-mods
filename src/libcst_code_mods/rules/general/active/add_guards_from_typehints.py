import attrs
import libcst as cst
import libcst.matchers as m

from libcst_code_mods.core.base_cst_transformer import BaseCstTransformer
from libcst_code_mods.core.base_cst_visitor import BaseCstVisitor
from libcst_code_mods.core.refactoring_rule import RefactoringRule
from libcst_code_mods.rules._rule_mapping import register_rule_transformer, register_rule_visitor


@attrs.define(frozen=True)
class AddGuardsFromTypehints(RefactoringRule):
    fn_names: list[str]


@register_rule_visitor(AddGuardsFromTypehints)
@attrs.define
class AddGuardsFromTypehintsVisitor(BaseCstVisitor):
    fn_names: list[str]

    def visit_FunctionDef(self, node: cst.FunctionDef) -> None:  # noqa: N802
        if node.name.value not in self.fn_names:
            return
        param_types = self.context.data.setdefault("param_types", {})
        param_types[node.name.value] = {
            p.name.value: p.annotation.annotation.value
            for p in node.params.params
            if m.matches(p.annotation, m.Annotation(m.Name()))
        }
        self.context.paths.add(self.path)


@register_rule_transformer(AddGuardsFromTypehints)
@attrs.define
class AddGuardsFromTypehintsTransformer(BaseCstTransformer):
    fn_names: list[str]
    param_types: dict[str, dict[str, str]]

    def leave_FunctionDef(self, original_node: cst.FunctionDef, updated_node: cst.FunctionDef) -> cst.FunctionDef:  # noqa: N802 ARG002
        if (
            updated_node.name.value not in self.fn_names
            or (fn_param_map := self.param_types.get(updated_node.name.value)) is None
        ):
            return updated_node

        isinstance_checks, type_err_expected = [], []

        for param, annot in fn_param_map.items():
            isinstance_checks.append(f"isinstance({param}, {annot})")
            type_err_expected.append(f"`{param}` expected `{annot}` got `{{type({param})}}`")

        msg = "Invalid arg types:\\n" + "\\n".join(type_err_expected)
        isinstance_checks_str = ", ".join(isinstance_checks)

        guards = cst.parse_statement(f"if not all([{isinstance_checks_str}]): raise TypeError(f'{msg}')")

        return updated_node.with_changes(body=updated_node.body.with_changes(body=[guards, *updated_node.body.body]))
