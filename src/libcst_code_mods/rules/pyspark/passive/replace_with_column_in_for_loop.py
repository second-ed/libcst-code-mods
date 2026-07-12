import attrs
import libcst as cst
import libcst.matchers as m

from libcst_code_mods.core.base_cst_transformer import BaseCstTransformer
from libcst_code_mods.core.base_cst_visitor import BaseCstVisitor
from libcst_code_mods.core.refactoring_rule import RefactoringRule
from libcst_code_mods.rules._rule_mapping import register_rule, register_rule_transformer, register_rule_visitor

from ._replace_with_column_in_for_loop import for_loop_matcher, update_with_column_call_in_for_loop


@register_rule
@attrs.define(frozen=True)
class ReplaceWithColumnInForLoop(RefactoringRule):
    """Examples:

        Case:

        Pre-transformer:

        .. code-block:: python

            def should_update_this_function() -> None:
                for col in ["a", "b", "c"]:
                    df = df.withColumn(col, lit(0))

        Post-transformer:

        .. code-block:: python

            def should_update_this_function() -> None:
                df = df.withColumns({col: lit(0) for col in ["a", "b", "c"]})


        Case:

        Pre-transformer:

        .. code-block:: python

            def correctly_updates_iterating_over_mapping() -> None:
                for col, expr in mapping.items():
                    df = df.withColumn(col, expr)

        Post-transformer:

        .. code-block:: python

            def correctly_updates_iterating_over_mapping() -> None:
                df = df.withColumns({col: expr for col, expr in mapping.items()})
    ::
    """


WITH_COLUMN_FOR_LOOP = for_loop_matcher("withColumn")


@register_rule_visitor(ReplaceWithColumnInForLoop)
@attrs.define
class ReplaceWithColumnInForLoopVisitor(BaseCstVisitor):
    def visit_For(self, node: cst.For) -> bool | None:  # noqa: N802
        if m.matches(node, WITH_COLUMN_FOR_LOOP):
            self.context.paths.add(self.path)
        return super().visit_For(node)


@register_rule_transformer(ReplaceWithColumnInForLoop)
@attrs.define
class ReplaceWithColumnInForLoopTransformer(BaseCstTransformer):
    def leave_For(  # noqa: N802
        self, original_node: cst.For, updated_node: cst.For
    ) -> cst.BaseExpression:
        return update_with_column_call_in_for_loop(original_node, updated_node, WITH_COLUMN_FOR_LOOP, "withColumns")
