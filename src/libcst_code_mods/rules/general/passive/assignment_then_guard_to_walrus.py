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

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def multiple_in_complex_condition() -> None:
                for i in range(10):
                    a = fn(i)
                    b = i + 1
                    if a is None or b is None:
                        continue

        Post-transformer:

        .. code-block:: python

            def multiple_in_complex_condition() -> None:
                for i in range(10):
                    if (a := fn(i)) is None or (b := i + 1) is None:
                        continue
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
COMPREHENSION_MATCHER = m.OneOf(m.GeneratorExp(), m.ListComp(), m.SetComp(), m.DictComp())


@register_rule_visitor(AssignmentThenGuardToWalrus)
@attrs.define
class AssignmentThenGuardToWalrusVisitor(BaseCstVisitor):
    def visit_IndentedBlock(self, node: cst.IndentedBlock) -> bool | None:  # noqa: N802
        if _find_assignment_and_guard_groups(node):
            self.context.paths.add(self.path)
        return super().visit_IndentedBlock(node)


@register_rule_transformer(AssignmentThenGuardToWalrus)
@attrs.define
class AssignmentThenGuardToWalrusTransformer(BaseCstTransformer):
    def leave_IndentedBlock(  # noqa: N802
        self, original_node: cst.IndentedBlock, updated_node: cst.IndentedBlock
    ) -> cst.IndentedBlock:
        if not (matches := _find_assignment_and_guard_groups(original_node)):
            return updated_node

        body = list(updated_node.body)
        for start_index, assignments, guard in reversed(matches):
            condition = guard["condition"]

            for extracted in assignments:
                target = extracted["target"]
                target_matcher = m.Name(value=target.value)
                walrus = cst.NamedExpr(target=target, value=extracted["value"])

                if not m.matches(condition, target_matcher):
                    walrus = walrus.with_changes(lpar=[cst.LeftParen()], rpar=[cst.RightParen()])

                if not m.matches(condition, target_matcher):
                    condition = condition.visit(_ReplaceName(name=target.value, replacement=walrus))
                    continue
                condition = walrus

            guard_node = body[start_index + len(assignments)].with_changes(
                leading_lines=original_node.body[start_index].leading_lines, test=condition
            )
            body[start_index : start_index + len(assignments) + 1] = [guard_node]

        return updated_node.with_changes(body=body)


def _find_assignment_and_guard_groups(
    node: cst.IndentedBlock,
) -> list[tuple[int, list[dict[str, cst.CSTNode]], dict[str, cst.CSTNode]]]:
    matches = []
    for guard_index, statement in enumerate(node.body):
        if (guard := m.extract(statement, GUARD_MATCHER)) is None:
            continue

        condition = guard["condition"]
        assignments = []
        assignment_index = guard_index - 1
        while assignment_index >= 0:
            if (assignment := m.extract(node.body[assignment_index], ASSIGNMENT_MATCHER)) is None:
                break
            if _target_occurrence_count(condition, assignment["target"].value) != 1:
                break
            assignments.append(assignment)
            assignment_index -= 1

        assignments.reverse()
        if not assignments:
            continue

        matches.append((assignment_index + 1, assignments, guard))

    return matches


def _target_occurrence_count(condition: cst.BaseExpression, target: str) -> int:
    if m.findall(condition, COMPREHENSION_MATCHER):
        return 0

    target_matcher = m.Name(value=target)
    if m.matches(condition, target_matcher):
        return 1

    return sum(
        len(matches)
        for matches in (
            m.findall(condition, m.UnaryOperation(expression=target_matcher)),
            m.findall(condition, m.Comparison(left=target_matcher)),
            m.findall(condition, m.Comparison(comparisons=[m.ComparisonTarget(comparator=target_matcher)])),
        )
    )


@attrs.define
class _ReplaceName(cst.CSTTransformer):
    name: str
    replacement: cst.NamedExpr

    def leave_Comparison(  # noqa: N802
        self, original_node: cst.Comparison, updated_node: cst.Comparison
    ) -> cst.Comparison:
        left = self.replacement if m.matches(original_node.left, m.Name(value=self.name)) else updated_node.left
        comparisons = [
            (
                comparison.with_changes(comparator=self.replacement)
                if m.matches(original_comparison.comparator, m.Name(value=self.name))
                else comparison
            )
            for original_comparison, comparison in zip(original_node.comparisons, updated_node.comparisons, strict=True)
        ]
        return updated_node.with_changes(left=left, comparisons=comparisons)

    def leave_UnaryOperation(  # noqa: N802
        self, original_node: cst.UnaryOperation, updated_node: cst.UnaryOperation
    ) -> cst.UnaryOperation:
        if m.matches(original_node.expression, m.Name(value=self.name)):
            return updated_node.with_changes(expression=self.replacement)
        return updated_node
