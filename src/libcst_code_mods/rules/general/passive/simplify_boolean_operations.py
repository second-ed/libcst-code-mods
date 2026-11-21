import attrs
import libcst as cst

from libcst_code_mods.core.base_cst_transformer import BaseCstTransformer
from libcst_code_mods.core.base_cst_visitor import BaseCstVisitor
from libcst_code_mods.core.refactoring_rule import RefactoringRule
from libcst_code_mods.cst_utils.boolean_algebra import BASIC_BOOLEAN_RULES, COMPOSITE_BOOLEAN_RULES, UNARY_BOOLEAN_RULES
from libcst_code_mods.rules._rule_mapping import register_rule, register_rule_transformer, register_rule_visitor


@register_rule
@attrs.frozen
class SimplifyBooleanOperations(RefactoringRule):
    """Examples:

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def identity_and() -> None:
                _ = A and True

        Post-transformer:

        .. code-block:: python

            def identity_and() -> None:
                _ = A

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def identity_or() -> None:
                _ = A or False

        Post-transformer:

        .. code-block:: python

            def identity_or() -> None:
                _ = A

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def domination_and() -> None:
                _ = A and False

        Post-transformer:

        .. code-block:: python

            def domination_and() -> None:
                _ = False

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def domination_or() -> None:
                _ = A or True

        Post-transformer:

        .. code-block:: python

            def domination_or() -> None:
                _ = True

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def idempotent_and() -> None:
                _ = A and A

        Post-transformer:

        .. code-block:: python

            def idempotent_and() -> None:
                _ = A

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def idempotent_or() -> None:
                _ = A or A

        Post-transformer:

        .. code-block:: python

            def idempotent_or() -> None:
                _ = A

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def complement_and() -> None:
                _ = A and not A

        Post-transformer:

        .. code-block:: python

            def complement_and() -> None:
                _ = False

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def complement_or() -> None:
                _ = A or not A

        Post-transformer:

        .. code-block:: python

            def complement_or() -> None:
                _ = True

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def absorption_or() -> None:
                _ = A or (A and B)

        Post-transformer:

        .. code-block:: python

            def absorption_or() -> None:
                _ = A

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def absorption_and() -> None:
                _ = A and (A or B)

        Post-transformer:

        .. code-block:: python

            def absorption_and() -> None:
                _ = A

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def double_negation() -> None:
                _ = not not A

        Post-transformer:

        .. code-block:: python

            def double_negation() -> None:
                _ = A

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def demorgan_and() -> None:
                _ = not (A and B)

        Post-transformer:

        .. code-block:: python

            def demorgan_and() -> None:
                _ = not A or not B

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def demorgan_or() -> None:
                _ = not (A or B)

        Post-transformer:

        .. code-block:: python

            def demorgan_or() -> None:
                _ = not A and not B

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def constant_not_true() -> None:
                _ = not True

        Post-transformer:

        .. code-block:: python

            def constant_not_true() -> None:
                _ = False

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def constant_not_false() -> None:
                _ = not False

        Post-transformer:

        .. code-block:: python

            def constant_not_false() -> None:
                _ = True

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def composite_identity_and_and_absorption_or() -> None:
                _ = (A and True) and (A or (A and B))

        Post-transformer:

        .. code-block:: python

            def composite_identity_and_and_absorption_or() -> None:
                _ = A

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def composite_factor_and_or() -> None:
                _ = (A and B) or (A and not B)

        Post-transformer:

        .. code-block:: python

            def composite_factor_and_or() -> None:
                _ = A

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def composite_factor_or_and() -> None:
                _ = (A or B) and (A or not B)

        Post-transformer:

        .. code-block:: python

            def composite_factor_or_and() -> None:
                _ = A

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def composite_factor_and_or_common_right() -> None:
                _ = (A and B) or (not A and B)

        Post-transformer:

        .. code-block:: python

            def composite_factor_and_or_common_right() -> None:
                _ = B

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def composite_factor_or_and_common_right() -> None:
                _ = (A or B) and (not A or B)

        Post-transformer:

        .. code-block:: python

            def composite_factor_or_and_common_right() -> None:
                _ = B

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def flattened_composite_factor() -> None:
                _ = (A and B and C) or (A and not B and C)

        Post-transformer:

        .. code-block:: python

            def flattened_composite_factor() -> None:
                _ = A and C

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            # more complex ones
            def composite_a() -> None:
                _ = (A or B) and (A or C)

        Post-transformer:

        .. code-block:: python

            # more complex ones
            def composite_a() -> None:
                _ = A or (B and C)

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def composite_b() -> None:
                _ = A and B and (not B and C or A and C)

        Post-transformer:

        .. code-block:: python

            def composite_b() -> None:
                _ = A and B and C

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def composite_c() -> None:
                _ = (A or not B or not C) and (A or not B or C) and (A or B or not C)

        Post-transformer:

        .. code-block:: python

            def composite_c() -> None:
                _ = A or not B and not C

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def more_absorption_law() -> None:
                _ = (A and B) or (A and not B) or (A and C)

        Post-transformer:

        .. code-block:: python

            def more_absorption_law() -> None:
                _ = A

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def demorgan_double_negation() -> None:
                _ = not (not A and not B) or not (A or B)

        Post-transformer:

        .. code-block:: python

            def demorgan_double_negation() -> None:
                _ = True

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def all_possible_branches() -> None:
                _ = (A and B) or (A and not B) or (not A and B) or (not A and not B)

        Post-transformer:

        .. code-block:: python

            def all_possible_branches() -> None:
                _ = True

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def conjunction_of_zero() -> None:
                _ = (A or B) and (A or not B) and (not A or C) and (not A or not C)

        Post-transformer:

        .. code-block:: python

            def conjunction_of_zero() -> None:
                _ = False

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def absorption_across_multiple_terms() -> None:
                _ = (A and B) or (A and C) or (B and C) or (A and B and C)

        Post-transformer:

        .. code-block:: python

            def absorption_across_multiple_terms() -> None:
                _ = A and (B or C) or (B and C)

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def simplify_four_terms() -> None:
                _ = not ((A and B) or (A and not B)) or (C and D) or (C and not D)

        Post-transformer:

        .. code-block:: python

            def simplify_four_terms() -> None:
                _ = C or not A
    ---
    """


@register_rule_visitor(SimplifyBooleanOperations)
@attrs.define
class SimplifyBooleanOperationsVisitor(BaseCstVisitor):
    def visit_BooleanOperation(self, node: cst.BooleanOperation) -> bool | None:  # noqa: N802
        self.context.paths.add(self.path)
        return super().visit_BooleanOperation(node)


@register_rule_transformer(SimplifyBooleanOperations)
@attrs.define
class SimplifyBooleanOperationsTransformer(BaseCstTransformer):
    def leave_BooleanOperation(  # noqa: N802
        self,
        original_node: cst.BooleanOperation,  # noqa: ARG002
        updated_node: cst.BooleanOperation,
    ) -> cst.BaseExpression:
        current: cst.BaseExpression = updated_node

        while isinstance(current, cst.BooleanOperation):
            previous = current

            for rule in BASIC_BOOLEAN_RULES + COMPOSITE_BOOLEAN_RULES:
                next_current = rule(current)

                if not isinstance(next_current, cst.BooleanOperation):
                    return next_current

                if not next_current.deep_equals(current):
                    return next_current.visit(self)

                current = next_current

            if current.deep_equals(previous):
                return current

        return current

    def leave_UnaryOperation(  # noqa: N802
        self,
        original_node: cst.UnaryOperation,  # noqa: ARG002
        updated_node: cst.UnaryOperation,
    ) -> cst.BaseExpression:
        current: cst.BaseExpression = updated_node

        while isinstance(current, cst.UnaryOperation):
            previous = current

            for rule in UNARY_BOOLEAN_RULES:
                next_current = rule(current)

                if not isinstance(next_current, cst.UnaryOperation):
                    return next_current.visit(self)

                if not next_current.deep_equals(current):
                    return next_current.visit(self)

                current = next_current

            if current.deep_equals(previous):
                return current

        return current
