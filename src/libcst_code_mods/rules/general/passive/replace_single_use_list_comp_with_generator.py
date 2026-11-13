import attrs
import libcst as cst
import libcst.matchers as m

from libcst_code_mods.core.base_cst_transformer import BaseCstTransformer
from libcst_code_mods.core.base_cst_visitor import BaseCstVisitor
from libcst_code_mods.core.refactoring_rule import RefactoringRule
from libcst_code_mods.rules._rule_mapping import register_rule, register_rule_transformer, register_rule_visitor


@register_rule
@attrs.frozen
class ReplaceSingleUseListCompWithGenerator(RefactoringRule):
    """Examples:

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def update_single_use_list_comp_to_gen_exp() -> None:
                values = [i + 1 for i in range(10)]
                sum(values)

        Post-transformer:

        .. code-block:: python

            def update_single_use_list_comp_to_gen_exp() -> None:
                values = (i + 1 for i in range(10))
                sum(values)
    ---
    """


ASSIGNMENT_MATCHER = m.SimpleStatementLine(
    body=[
        m.Assign(
            targets=[m.AssignTarget(target=m.SaveMatchedNode(m.Name(), "name"))],
            value=m.SaveMatchedNode(m.ListComp(), "value"),
        )
    ]
)


@register_rule_visitor(ReplaceSingleUseListCompWithGenerator)
@attrs.define
class ReplaceSingleUseListCompWithGeneratorVisitor(BaseCstVisitor):
    def visit_FunctionDef(self, node: cst.FunctionDef) -> bool | None:  # noqa: N802
        if m.findall(node.body, ASSIGNMENT_MATCHER):
            self.context.paths.add(self.path)
        return super().visit_FunctionDef(node)


@register_rule_transformer(ReplaceSingleUseListCompWithGenerator)
@attrs.define
class ReplaceSingleUseListCompWithGeneratorTransformer(BaseCstTransformer):
    def leave_FunctionDef(  # noqa: N802
        self,
        original_node: cst.FunctionDef,  # noqa: ARG002
        updated_node: cst.FunctionDef,
    ) -> cst.FunctionDef:
        new_body = [_update_statement(updated_node, updated_statement) for updated_statement in updated_node.body.body]

        return updated_node.with_changes(body=updated_node.body.with_changes(body=new_body))


def _to_generator(value: cst.BaseExpression) -> cst.BaseExpression:
    if not m.matches(value, m.ListComp()):
        return value
    return cst.GeneratorExp(elt=value.elt, for_in=value.for_in)


def _update_statement(
    updated_node: cst.FunctionDef, updated_statement: cst.BaseStatement | cst.BaseSmallStatement
) -> cst.BaseStatement | cst.BaseSmallStatement:
    if (
        not m.matches(updated_statement, ASSIGNMENT_MATCHER)
        or (extracted := m.extract(updated_statement, ASSIGNMENT_MATCHER)) is None
    ):
        return updated_statement

    name = extracted["name"]
    names = m.findall(updated_node.body, m.Name(value=name.value))
    target_assignments = m.findall(updated_node.body, m.AssignTarget(target=m.Name(value=name.value)))
    assignment_targets = {target.target for target in target_assignments}
    keyword_names = {
        argument.keyword for argument in m.findall(updated_node.body, m.Arg(keyword=m.Name(value=name.value)))
    }
    attribute_names = {
        attribute.attr for attribute in m.findall(updated_node.body, m.Attribute(attr=m.Name(value=name.value)))
    }
    uses = [
        node
        for node in names
        if node not in assignment_targets and node not in keyword_names and node not in attribute_names
    ]
    if len(target_assignments) != 1 or len(uses) != 1:
        return updated_statement

    assignment = updated_statement.body[0]
    return updated_statement.with_changes(body=[assignment.with_changes(value=_to_generator(assignment.value))])
