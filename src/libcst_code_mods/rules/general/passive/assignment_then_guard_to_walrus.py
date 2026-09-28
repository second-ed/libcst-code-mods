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

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def multiple_to_change() -> None:
                if unrelated_condition:
                    return

                res = fn()
                if res is None:
                    return
                fn_2(res)

                res_2 = fn_2()
                if res_2 is not None:
                    return res_2

                res_3 = fn_3()
                if not res_3:
                    return
                fn_3_output(res_3)

                res_4 = fn_4()
                if res_4:
                    return res_4

        Post-transformer:

        .. code-block:: python

            def multiple_to_change() -> None:
                if unrelated_condition:
                    return

                if (res := fn()) is None:
                    return
                fn_2(res)

                if (res_2 := fn_2()) is not None:
                    return res_2

                if not (res_3 := fn_3()):
                    return
                fn_3_output(res_3)

                if res_4 := fn_4():
                    return res_4

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def make_slots_decorator(decorator: cst.Decorator) -> cst.Decorator:
                matched = m.extract(decorator, m.Decorator(decorator=m.SaveMatchedNode(m.Call(), "call")))
                if matched is None:
                    return decorator
                return decorator.with_changes()

        Post-transformer:

        .. code-block:: python

            def make_slots_decorator(decorator: cst.Decorator) -> cst.Decorator:
                if (matched := m.extract(decorator, m.Decorator(decorator=m.SaveMatchedNode(m.Call(), "call")))) is None:
                    return decorator
                return decorator.with_changes()
    ---
    """


ASSIGNMENT_MATCHER = m.SimpleStatementLine(
    body=[
        m.Assign(
            targets=[m.AssignTarget(target=m.SaveMatchedNode(m.Name(), "target"))],
            value=m.SaveMatchedNode(m.DoNotCare(), "value"),
        )
    ]
)

GUARD_MATCHER = m.If(test=m.SaveMatchedNode(m.DoNotCare(), "condition"))


@register_rule_visitor(AssignmentThenGuardToWalrus)
@attrs.define
class AssignmentThenGuardToWalrusVisitor(BaseCstVisitor):
    def visit_IndentedBlock(self, node: cst.IndentedBlock) -> bool | None:  # noqa: N802
        if _find_assignment_and_guards(node):
            self.context.paths.add(self.path)
        return super().visit_IndentedBlock(node)


@register_rule_transformer(AssignmentThenGuardToWalrus)
@attrs.define
class AssignmentThenGuardToWalrusTransformer(BaseCstTransformer):
    def leave_IndentedBlock(  # noqa: N802
        self, original_node: cst.IndentedBlock, updated_node: cst.IndentedBlock
    ) -> cst.IndentedBlock:
        if not (matches := _find_assignment_and_guards(original_node)):
            return updated_node

        body = list(updated_node.body)
        for assignment_index, extracted in reversed(matches):
            target = extracted["target"]
            condition = extracted["condition"]
            target_matcher = m.Name(value=target.value)
            walrus = cst.NamedExpr(target=target, value=extracted["value"])
            if not m.matches(condition, target_matcher):
                walrus = walrus.with_changes(lpar=[cst.LeftParen()], rpar=[cst.RightParen()])

            new_condition = condition.visit(_ReplaceName(name=target.value, replacement=walrus))
            guard = body[assignment_index + 1].with_changes(
                leading_lines=original_node.body[assignment_index].leading_lines, test=new_condition
            )
            body[assignment_index : assignment_index + 2] = [guard]

        return updated_node.with_changes(body=body)


def _find_assignment_and_guards(node: cst.IndentedBlock) -> list[tuple[int, dict[str, cst.CSTNode]]]:
    matches = []
    for index in range(len(node.body) - 1):
        assignment = m.extract(node.body[index], ASSIGNMENT_MATCHER)
        guard = m.extract(node.body[index + 1], GUARD_MATCHER)
        if assignment is None or guard is None:
            continue

        extracted = {**assignment, **guard}
        target = extracted["target"]
        condition = extracted["condition"]
        target_matcher = m.Name(value=target.value)
        if (
            m.matches(condition, target_matcher)
            or m.matches(condition, m.UnaryOperation(operator=m.Not(), expression=target_matcher))
            or m.matches(condition, m.Comparison(left=target_matcher))
        ):
            matches.append((index, extracted))

    return matches


@attrs.define
class _ReplaceName(cst.CSTTransformer):
    name: str
    replacement: cst.NamedExpr

    def leave_Name(self, original_node: cst.Name, updated_node: cst.Name) -> cst.BaseExpression:  # noqa: N802
        if original_node.value == self.name:
            return self.replacement
        return updated_node
