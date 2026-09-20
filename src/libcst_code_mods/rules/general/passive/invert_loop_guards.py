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
    """Examples:

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def simple_loop_with_if_else() -> None:
                for i in range(10):
                    if i % 2 == 0:
                        print(f"{i} is even")
                    else:
                        print(f"{i} is odd")

        Post-transformer:

        .. code-block:: python

            def simple_loop_with_if_else() -> None:
                for i in range(10):
                    if i % 2 != 0:
                        print(f"{i} is odd")
                        continue
                    print(f"{i} is even")

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def loop_with_extra_statements_and_if_else() -> None:
                for i in range(10):
                    x = 2
                    y = 0
                    y += x
                    if i % 2 == 0:
                        print(f"{i} is even")
                    else:
                        print(f"{i} is odd")

        Post-transformer:

        .. code-block:: python

            def loop_with_extra_statements_and_if_else() -> None:
                for i in range(10):
                    x = 2
                    y = 0
                    y += x
                    if i % 2 != 0:
                        print(f"{i} is odd")
                        continue
                    print(f"{i} is even")
    ---
    """


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
    def leave_For(self, _original_node: cst.For, updated_node: cst.For) -> cst.For | cst.FlattenSentinel:  # noqa: N802

        if not (extracted := m.extract(updated_node, GUARD_MATCHER)):
            return updated_node

        if updated_node.body.body[-1] != extracted["if_node"]:
            return updated_node

        guard = cst.If(
            test=invert_condition(extracted["condition"]),
            body=cst.IndentedBlock(
                body=[*extracted["failure_body"].body, cst.SimpleStatementLine(body=[cst.Continue()])]
            ),
        )
        return updated_node.with_changes(
            body=updated_node.body.with_changes(
                body=[*extracted["existing_body"], guard, *extracted["success_body"].body]
            )
        )
