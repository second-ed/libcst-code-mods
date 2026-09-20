import attrs
import libcst as cst
import libcst.matchers as m

from libcst_code_mods.core.base_cst_transformer import BaseCstTransformer
from libcst_code_mods.core.base_cst_visitor import BaseCstVisitor
from libcst_code_mods.core.refactoring_rule import RefactoringRule
from libcst_code_mods.rules._rule_mapping import register_rule, register_rule_transformer, register_rule_visitor


@register_rule
@attrs.define(frozen=True)
class InlineShortSingleUseVariables(RefactoringRule):
    """Examples:

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def single_use_variable_is_inlined() -> None:
                a = "something"
                b = fn(a=a)

        Post-transformer:

        .. code-block:: python

            def single_use_variable_is_inlined() -> None:
                b = fn(a="something")

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def single_use_list_comp_is_inlined() -> None:
                a = [f(x) for x in y]
                b = fn(a=a)

        Post-transformer:

        .. code-block:: python

            def single_use_list_comp_is_inlined() -> None:
                b = fn(a=[f(x) for x in y])
    ---
    """

    max_value_length: int = 30


ASSIGNMENT_MATCHER = m.SimpleStatementLine(
    body=[
        m.Assign(
            targets=[m.AssignTarget(target=m.SaveMatchedNode(m.Name(), "name"))],
            value=m.SaveMatchedNode(m.DoNotCare(), "value"),
        )
    ]
)


@register_rule_visitor(InlineShortSingleUseVariables)
@attrs.define
class InlineShortSingleUseVariablesVisitor(BaseCstVisitor):
    def visit_FunctionDef(self, node: cst.FunctionDef) -> bool | None:  # noqa: N802
        if m.findall(node.body, ASSIGNMENT_MATCHER):
            self.context.paths.add(self.path)
        return super().visit_FunctionDef(node)


@register_rule_transformer(InlineShortSingleUseVariables)
@attrs.define
class InlineShortSingleUseVariablesTransformer(BaseCstTransformer):
    max_value_length: int

    def leave_FunctionDef(  # noqa: N802
        self, original_node: cst.FunctionDef, updated_node: cst.FunctionDef
    ) -> cst.FunctionDef:
        assignments = m.findall(original_node.body, ASSIGNMENT_MATCHER)
        if not assignments:
            return updated_node

        inlineable = []
        for assignment in assignments:
            extracted = m.extract(assignment, ASSIGNMENT_MATCHER)
            name = extracted["name"]
            value = extracted["value"]
            if len(cst.Module([]).code_for_node(value)) > self.max_value_length:
                continue

            uses = m.findall(original_node.body, m.Arg(value=m.Name(value=name.value)))
            if len(uses) != 1:
                continue

            assignment_index = original_node.body.body.index(assignment)
            inlineable.append((assignment_index, name.value, value))

        body = list(updated_node.body.body)
        for assignment_index, name, value in reversed(inlineable):
            body = [
                statement.visit(_ReplaceName(name=name, replacement=value))
                for index, statement in enumerate(body)
                if index != assignment_index
            ]
        return updated_node.with_changes(body=updated_node.body.with_changes(body=body))


@attrs.define
class _ReplaceName(cst.CSTTransformer):
    name: str
    replacement: cst.BaseExpression

    def leave_Arg(self, original_node: cst.Arg, updated_node: cst.Arg) -> cst.Arg:  # noqa: N802
        if m.matches(original_node, m.Arg(value=m.Name(self.name))):
            return updated_node.with_changes(value=self.replacement)
        return updated_node
