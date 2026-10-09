import attrs
import libcst as cst

from libcst_code_mods.core.base_cst_transformer import BaseCstTransformer
from libcst_code_mods.core.base_cst_visitor import BaseCstVisitor
from libcst_code_mods.core.refactoring_rule import RefactoringRule
from libcst_code_mods.rules._cst_utils import visit_for_if_matches
from libcst_code_mods.rules._rule_mapping import register_rule, register_rule_transformer, register_rule_visitor

from ._replace_with_column_in_for_loop import for_loop_matcher, update_with_column_call_in_for_loop


@register_rule
@attrs.define(frozen=True)
class ReplaceWithColumnRenamedInForLoop(RefactoringRule):
    """Examples:

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def should_update_this_function() -> None:
                for col in ["a", "b", "c"]:
                    df = df.withColumnRenamed(col, f"{col}_new")

        Post-transformer:

        .. code-block:: python

            def should_update_this_function() -> None:
                df = df.withColumnsRenamed({col: f"{col}_new" for col in ["a", "b", "c"]})

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def correctly_updates_iterating_over_mapping() -> None:
                for old, new in mapping.items():
                    df = df.withColumnRenamed(old, new)

        Post-transformer:

        .. code-block:: python

            def correctly_updates_iterating_over_mapping() -> None:
                df = df.withColumnsRenamed({old: new for old, new in mapping.items()})
    ---
    """


WITH_COLUMN_FOR_LOOP = for_loop_matcher("withColumnRenamed")


@register_rule_visitor(ReplaceWithColumnRenamedInForLoop)
@attrs.define
class ReplaceWithColumnRenamedInForLoopVisitor(BaseCstVisitor):
    def visit_For(self, node: cst.For) -> bool | None:  # noqa: N802
        return visit_for_if_matches(self, node, WITH_COLUMN_FOR_LOOP, super().visit_For)


@register_rule_transformer(ReplaceWithColumnRenamedInForLoop)
@attrs.define
class ReplaceWithColumnRenamedInForLoopTransformer(BaseCstTransformer):
    def leave_For(  # noqa: N802
        self, original_node: cst.For, updated_node: cst.For
    ) -> cst.BaseExpression:
        return update_with_column_call_in_for_loop(
            original_node, updated_node, WITH_COLUMN_FOR_LOOP, "withColumnsRenamed"
        )
