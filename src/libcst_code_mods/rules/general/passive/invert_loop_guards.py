import attrs
import libcst as cst
import libcst.matchers as m

from libcst_code_mods.core.base_cst_transformer import BaseCstTransformer
from libcst_code_mods.core.base_cst_visitor import BaseCstVisitor
from libcst_code_mods.core.refactoring_rule import RefactoringRule
from libcst_code_mods.rules._cst_utils import invert_condition
from libcst_code_mods.rules._rule_mapping import register_rule, register_rule_transformer, register_rule_visitor


@register_rule
@attrs.define(frozen=True)
class InvertLoopGuards(RefactoringRule):
    pass


GUARD_MATCHER = m.For(
    body=m.IndentedBlock(
        body=[
            m.SaveMatchedNode(m.ZeroOrMore(), "existing_body"),
            m.SaveMatchedNode(
                m.If(
                    test=m.SaveMatchedNode(m.DoNotCare(), "condition"),
                    body=m.SaveMatchedNode(m.IndentedBlock(), "success_body"),
                    orelse=m.Else(m.SaveMatchedNode(m.IndentedBlock(), "failure_body")),
                ),
                "if_node",
            ),
        ]
    )
)


@register_rule_visitor(InvertLoopGuards)
@attrs.define
class InvertLoopGuardsVisitor(BaseCstVisitor):
    def visit_For(self, node: cst.For) -> bool | None:  # noqa: N802
        if m.matches(node, GUARD_MATCHER):
            self.context.paths.add(self.path)
        return super().visit_For(node)


@register_rule_transformer(InvertLoopGuards)
@attrs.define
class InvertLoopGuardsTransformer(BaseCstTransformer):
    def leave_For(self, original_node: cst.For, updated_node: cst.For) -> cst.For | cst.FlattenSentinel:  # noqa: N802 ARG002
        extracted = m.extract(updated_node, GUARD_MATCHER)

        if not extracted:
            return updated_node

        block_body = list(updated_node.body.body)

        if block_body[-1] != extracted["if_node"]:
            return updated_node

        condition = extracted["condition"]
        success_body = list(extracted["success_body"].body)
        failure_body = list(extracted["failure_body"].body)

        guard = cst.If(
            test=invert_condition(condition),
            body=cst.IndentedBlock(body=[*failure_body, cst.SimpleStatementLine(body=[cst.Continue()])]),
        )
        return updated_node.with_changes(
            body=updated_node.body.with_changes(body=[*extracted["existing_body"], guard, *success_body])
        )
