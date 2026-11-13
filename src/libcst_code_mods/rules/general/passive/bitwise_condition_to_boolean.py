from collections.abc import Collection
from typing import ClassVar

import attrs
import libcst as cst

from libcst_code_mods.core.base_cst_transformer import BaseCstTransformer
from libcst_code_mods.core.base_cst_visitor import BaseCstVisitor
from libcst_code_mods.core.refactoring_rule import RefactoringRule
from libcst_code_mods.rules._rule_mapping import register_rule, register_rule_transformer, register_rule_visitor


@register_rule
@attrs.frozen
class BitwiseConditionToBoolean(RefactoringRule):
    """Examples:

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def if_stmt_to_and() -> None:
                if 1 == 1 & 2 == 2:
                    print("condition is true")

        Post-transformer:

        .. code-block:: python

            def if_stmt_to_and() -> None:
                if 1 == 1 and 2 == 2:
                    print("condition is true")

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def if_stmt_to_or() -> None:
                if 1 == 1 | 2 == 2:
                    print("condition is true")

        Post-transformer:

        .. code-block:: python

            def if_stmt_to_or() -> None:
                if 1 == 1 or 2 == 2:
                    print("condition is true")

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def multiple_conds_with_ands_and_ors() -> None:
                if (1 == 1 & 2 == 2) & (1 == 1 | 2 == 2):
                    print("condition is true")
                elif 1 == 1 & 2 == 2 | 3 == 3:
                    print("condition is true")

        Post-transformer:

        .. code-block:: python

            def multiple_conds_with_ands_and_ors() -> None:
                if (1 == 1 and 2 == 2) and (1 == 1 or 2 == 2):
                    print("condition is true")
                elif 1 == 1 and 2 == 2 or 3 == 3:
                    print("condition is true")

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def should_not_change_if_bitwise_is_not_top_level(df) -> None:
                if df[df["a"] & df["b"]].all():
                    print("condition is true")
                elif df.filter(col("a") & col("b")).all():
                    print("condition is true")
                elif df.filter(col("a") & col("b")).all() & 1 == 1:
                    print("condition is true")

        Post-transformer:

        .. code-block:: python

            def should_not_change_if_bitwise_is_not_top_level(df) -> None:
                if df[df["a"] & df["b"]].all():
                    print("condition is true")
                elif df.filter(col("a") & col("b")).all():
                    print("condition is true")
                elif df.filter(col("a") & col("b")).all() and 1 == 1:
                    print("condition is true")
    ---
    """


@register_rule_visitor(BitwiseConditionToBoolean)
@attrs.define
class BitwiseConditionToBooleanVisitor(BaseCstVisitor):
    METADATA_DEPENDENCIES: ClassVar[Collection[cst.metadata.ProviderT]] = (cst.metadata.ParentNodeProvider,)

    def visit_BinaryOperation(self, node: cst.BinaryOperation) -> bool:  # noqa: N802
        if isinstance(node.operator, (cst.BitAnd, cst.BitOr)) and _is_if_condition(self, node):
            self.context.paths.add(self.path)
        return True


@register_rule_transformer(BitwiseConditionToBoolean)
@attrs.define
class BitwiseConditionToBooleanTransformer(BaseCstTransformer):
    METADATA_DEPENDENCIES: ClassVar[Collection[cst.metadata.ProviderT]] = (cst.metadata.ParentNodeProvider,)

    def leave_BinaryOperation(  # noqa: N802
        self, original_node: cst.BinaryOperation, updated_node: cst.BinaryOperation
    ) -> cst.BaseExpression:
        if not _is_if_condition(self, original_node):
            return updated_node

        if (operator_type := BITWISE_TO_BOOLEAN_OPERATOR.get(type(updated_node.operator))) is None:
            return updated_node
        operator = operator_type(
            whitespace_before=updated_node.operator.whitespace_before,
            whitespace_after=updated_node.operator.whitespace_after,
        )

        return cst.BooleanOperation(
            left=updated_node.left,
            operator=operator,
            right=updated_node.right,
            lpar=updated_node.lpar,
            rpar=updated_node.rpar,
        )


def _is_if_condition(node_provider: BaseCstVisitor | BaseCstTransformer, node: cst.CSTNode) -> bool:
    current = node
    while (parent := node_provider.get_metadata(cst.metadata.ParentNodeProvider, current, None)) is not None:
        if isinstance(parent, (cst.Call, cst.Subscript)):
            return False
        if isinstance(parent, cst.If):
            return parent.test is current
        current = parent
    return False


BITWISE_TO_BOOLEAN_OPERATOR: dict[type[cst.BitAnd | cst.BitOr], type[cst.And | cst.Or]] = {
    cst.BitAnd: cst.And,
    cst.BitOr: cst.Or,
}
