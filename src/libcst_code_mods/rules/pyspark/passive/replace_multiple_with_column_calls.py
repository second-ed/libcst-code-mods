import attrs
import libcst as cst
import libcst.matchers as m

from libcst_code_mods.core.base_cst_transformer import BaseCstTransformer
from libcst_code_mods.core.base_cst_visitor import BaseCstVisitor
from libcst_code_mods.core.refactoring_rule import RefactoringRule
from libcst_code_mods.rules._rule_mapping import register_rule, register_rule_transformer, register_rule_visitor

from ._replace_multiple_with_column_calls import update_multiple_with_column_calls


@register_rule
@attrs.define(frozen=True)
class ReplaceMultipleWithColumnCalls(RefactoringRule):
    """Examples:

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def two_with_column_calls_in_a_row() -> None:
                df.withColumn("a", lit(1)).withColumn("b", col("blah"))

        Post-transformer:

        .. code-block:: python

            def two_with_column_calls_in_a_row() -> None:
                df.withColumns({"a": lit(1), "b": col("blah")})

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def three_with_column_calls_in_a_row() -> None:
                df.withColumn("a", lit(1)).withColumn("b", col("blah")).withColumn("c", lit(3))

        Post-transformer:

        .. code-block:: python

            def three_with_column_calls_in_a_row() -> None:
                df.withColumns({"a": lit(1), "b": col("blah"), "c": lit(3)})

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def with_column_chain_assigned() -> None:
                result = df.withColumn("a", lit(1)).withColumn("b", col("blah")).withColumn("c", upper(col("name")))

        Post-transformer:

        .. code-block:: python

            def with_column_chain_assigned() -> None:
                result = df.withColumns({"a": lit(1), "b": col("blah"), "c": upper(col("name"))})

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def with_column_chain_after_filter() -> None:
                df.filter(col("active")).withColumn("a", lit(1)).withColumn("b", col("blah"))

        Post-transformer:

        .. code-block:: python

            def with_column_chain_after_filter() -> None:
                df.filter(col("active")).withColumns({"a": lit(1), "b": col("blah")})

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def with_column_chain_inside_return() -> None:
                return (
                    df.withColumn("a", lit(1)).withColumn("b", col("blah")).withColumn("c", concat(col("x"), col("y")))
                )

        Post-transformer:

        .. code-block:: python

            def with_column_chain_inside_return() -> None:
                return df.withColumns({"a": lit(1), "b": col("blah"), "c": concat(col("x"), col("y"))})

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def with_column_chain_followed_by_select() -> None:
                df.withColumn("a", lit(1)).withColumn("b", col("blah")).select("a", "b")

        Post-transformer:

        .. code-block:: python

            def with_column_chain_followed_by_select() -> None:
                df.withColumns({"a": lit(1), "b": col("blah")}).select("a", "b")
    ---
    """


WITH_COLUMN_ATTR = m.Attribute(attr=m.Name("withColumn"))
WITH_COLUMN_CALL = m.Call(func=WITH_COLUMN_ATTR)


@register_rule_visitor(ReplaceMultipleWithColumnCalls)
@attrs.define
class ReplaceMultipleWithColumnCallsVisitor(BaseCstVisitor):
    def visit_Call(self, node: cst.Call) -> bool | None:  # noqa: N802
        if m.matches(node, WITH_COLUMN_CALL):
            self.context.paths.add(self.path)
        return super().visit_Call(node)


@register_rule_transformer(ReplaceMultipleWithColumnCalls)
@attrs.define
class ReplaceMultipleWithColumnCallsTransformer(BaseCstTransformer):
    def leave_Call(self, original_node: cst.Call, updated_node: cst.Call) -> cst.BaseExpression:  # noqa: N802
        return update_multiple_with_column_calls(
            self, original_node, updated_node, WITH_COLUMN_CALL, WITH_COLUMN_ATTR, "withColumns"
        )
