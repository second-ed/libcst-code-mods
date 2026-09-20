import attrs
import libcst as cst
import libcst.matchers as m

from libcst_code_mods.core.base_cst_transformer import BaseCstTransformer
from libcst_code_mods.core.base_cst_visitor import BaseCstVisitor
from libcst_code_mods.core.refactoring_rule import RefactoringRule
from libcst_code_mods.rules._rule_mapping import register_rule, register_rule_transformer, register_rule_visitor


@register_rule
@attrs.define(frozen=True)
class AssignmentThenGuardToWalrus(RefactoringRule):
    """Examples:

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def checks_if_is_none() -> None:
                res = fn()
                if res is None:
                    return
                fn_2(res)

        Post-transformer:

        .. code-block:: python

            def checks_if_is_none() -> None:
                if (res := fn()) is None:
                    return
                fn_2(res)

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def checks_if_is_not_none() -> Any:
                res = fn()
                if res is not None:
                    return res

        Post-transformer:

        .. code-block:: python

            def checks_if_is_not_none() -> Any:
                if (res := fn()) is not None:
                    return res

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def checks_if_is_not_truthy() -> None:
                res = fn()
                if not res:
                    return
                fn_2(res)

        Post-transformer:

        .. code-block:: python

            def checks_if_is_not_truthy() -> None:
                if not (res := fn()):
                    return
                fn_2(res)

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def checks_if_is_truthy() -> Any | None:
                res = fn()
                if res:
                    return res

        Post-transformer:

        .. code-block:: python

            def checks_if_is_truthy() -> Any | None:
                if res := fn():
                    return res
    ---
    """


ASSIGNMENT_THEN_GUARD_MATCHER = m.IndentedBlock(
    body=[
        m.SaveMatchedNode(m.ZeroOrMore(), "before"),
        m.SaveMatchedNode(
            m.SimpleStatementLine(
                body=[
                    m.Assign(
                        targets=[m.AssignTarget(target=m.SaveMatchedNode(m.Name(), "target"))],
                        value=m.SaveMatchedNode(m.DoNotCare(), "value"),
                    )
                ]
            ),
            "assignment",
        ),
        m.SaveMatchedNode(m.If(test=m.SaveMatchedNode(m.DoNotCare(), "condition")), "guard"),
        m.SaveMatchedNode(m.ZeroOrMore(), "after"),
    ]
)


@register_rule_visitor(AssignmentThenGuardToWalrus)
@attrs.define
class AssignmentThenGuardToWalrusVisitor(BaseCstVisitor):
    def visit_IndentedBlock(self, node: cst.IndentedBlock) -> bool | None:  # noqa: N802
        if m.matches(node, ASSIGNMENT_THEN_GUARD_MATCHER):
            self.context.paths.add(self.path)
        return super().visit_IndentedBlock(node)


@register_rule_transformer(AssignmentThenGuardToWalrus)
@attrs.define
class AssignmentThenGuardToWalrusTransformer(BaseCstTransformer):
    def leave_IndentedBlock(  # noqa: N802
        self, original_node: cst.IndentedBlock, updated_node: cst.IndentedBlock
    ) -> cst.IndentedBlock:
        extracted = m.extract(original_node, ASSIGNMENT_THEN_GUARD_MATCHER)
        if extracted is None:
            return updated_node

        target = extracted["target"]
        condition = extracted["condition"]
        target_matcher = m.Name(value=target.value)
        if not (
            m.matches(condition, target_matcher)
            or m.matches(condition, m.UnaryOperation(operator=m.Not(), expression=target_matcher))
            or m.matches(condition, m.Comparison(left=target_matcher))
        ):
            return updated_node

        walrus = cst.NamedExpr(target=target, value=extracted["value"])
        if not m.matches(condition, target_matcher):
            walrus = walrus.with_changes(lpar=[cst.LeftParen()], rpar=[cst.RightParen()])

        new_condition = condition.visit(_ReplaceName(name=target.value, replacement=walrus))
        guard = extracted["guard"].with_changes(test=new_condition)
        body = list(updated_node.body)
        guard_index = original_node.body.index(extracted["guard"])
        body[guard_index - 1 : guard_index + 1] = [guard]
        return updated_node.with_changes(body=body)


@attrs.define
class _ReplaceName(cst.CSTTransformer):
    name: str
    replacement: cst.NamedExpr

    def leave_Name(self, original_node: cst.Name, updated_node: cst.Name) -> cst.BaseExpression:  # noqa: N802
        if original_node.value == self.name:
            return self.replacement
        return updated_node
