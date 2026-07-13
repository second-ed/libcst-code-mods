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
class ReplaceMultipleWithColumnRenamedCalls(RefactoringRule):
    """Examples:

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def two_with_column_renamed_calls_in_a_row() -> None:
                df.withColumnRenamed("a", "x").withColumnRenamed("b", "y")

        Post-transformer:

        .. code-block:: python

            def two_with_column_renamed_calls_in_a_row() -> None:
                df.withColumnsRenamed({"a": "x", "b": "y"})

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def three_with_column_renamed_calls_in_a_row() -> None:
                df.withColumnRenamed("a", "x").withColumnRenamed("b", "y").withColumnRenamed("c", "z")

        Post-transformer:

        .. code-block:: python

            def three_with_column_renamed_calls_in_a_row() -> None:
                df.withColumnsRenamed({"a": "x", "b": "y", "c": "z"})

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def with_column_renamed_chain_assigned() -> None:
                result = df.withColumnRenamed("first_name", "forename").withColumnRenamed("last_name", "surname")

        Post-transformer:

        .. code-block:: python

            def with_column_renamed_chain_assigned() -> None:
                result = df.withColumnsRenamed({"first_name": "forename", "last_name": "surname"})

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def with_column_renamed_chain_after_filter() -> None:
                df.filter(col("active")).withColumnRenamed("a", "x").withColumnRenamed("b", "y")

        Post-transformer:

        .. code-block:: python

            def with_column_renamed_chain_after_filter() -> None:
                df.filter(col("active")).withColumnsRenamed({"a": "x", "b": "y"})

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def with_column_renamed_chain_inside_return() -> None:
                return df.withColumnRenamed("a", "x").withColumnRenamed("b", "y").withColumnRenamed("c", "z")

        Post-transformer:

        .. code-block:: python

            def with_column_renamed_chain_inside_return() -> None:
                return df.withColumnsRenamed({"a": "x", "b": "y", "c": "z"})

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def with_column_renamed_chain_followed_by_select() -> None:
                df.withColumnRenamed("a", "x").withColumnRenamed("b", "y").select("x", "y")

        Post-transformer:

        .. code-block:: python

            def with_column_renamed_chain_followed_by_select() -> None:
                df.withColumnsRenamed({"a": "x", "b": "y"}).select("x", "y")
    ---
    """


WITH_COLUMN_ATTR = m.Attribute(attr=m.Name("withColumnRenamed"))
WITH_COLUMN_CALL = m.Call(func=WITH_COLUMN_ATTR)


@register_rule_visitor(ReplaceMultipleWithColumnRenamedCalls)
@attrs.define
class ReplaceMultipleWithColumnRenamedCallsVisitor(BaseCstVisitor):
    def visit_Call(self, node: cst.Call) -> bool | None:  # noqa: N802
        if m.matches(node, WITH_COLUMN_CALL):
            self.context.paths.add(self.path)
        return super().visit_Call(node)


@register_rule_transformer(ReplaceMultipleWithColumnRenamedCalls)
@attrs.define
class ReplaceMultipleWithColumnRenamedCallsTransformer(BaseCstTransformer):
    def leave_Call(  # noqa: N802
        self, original_node: cst.Call, updated_node: cst.Call
    ) -> cst.BaseExpression:
        return update_multiple_with_column_calls(
            self, original_node, updated_node, WITH_COLUMN_CALL, WITH_COLUMN_ATTR, "withColumnsRenamed"
        )
