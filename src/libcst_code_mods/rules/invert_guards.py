import attrs
import libcst as cst
import libcst.matchers as m

from libcst_code_mods.core.base_cst_transformer import BaseCstTransformer
from libcst_code_mods.core.refactoring_rule import RefactoringRule
from libcst_code_mods.rules._rule_mapping import register_rule_transformer


@attrs.define(frozen=True)
class InvertGuards(RefactoringRule):
    pass


GUARD_MATCHER = m.If(
    test=m.SaveMatchedNode(m.DoNotCare(), "condition"),
    body=m.SaveMatchedNode(m.IndentedBlock(), "success_body"),
    orelse=m.Else(
        body=m.SaveMatchedNode(
            m.IndentedBlock(body=[m.ZeroOrMore(), m.SimpleStatementLine(body=[m.OneOf(m.Return(), m.Raise())])]),
            "failure_body",
        )
    ),
)


@register_rule_transformer(InvertGuards)
@attrs.define
class InvertGuardsTransformer(BaseCstTransformer):
    def leave_If(self, original_node: cst.If, updated_node: cst.If) -> cst.If | cst.FlattenSentinel:  # noqa: N802 ARG002
        extracted = m.extract(updated_node, GUARD_MATCHER)

        if not extracted:
            return updated_node

        condition = extracted["condition"]
        success_body = list(extracted["success_body"].body)
        failure_body = list(extracted["failure_body"].body)

        if not failure_body:
            return updated_node

        last = failure_body[-1]

        if not isinstance(last, cst.SimpleStatementLine) or not isinstance(last.body[0], (cst.Return, cst.Raise)):
            return updated_node

        guard = cst.If(test=invert_condition(condition), body=cst.IndentedBlock(body=failure_body))
        return cst.FlattenSentinel([guard, *success_body])


def invert_condition(expr: cst.BaseExpression) -> cst.BaseExpression:
    return cst.UnaryOperation(operator=cst.Not(), expression=expr)
