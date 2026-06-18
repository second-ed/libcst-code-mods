import attrs
import libcst as cst
import libcst.matchers as m

from libcst_code_mods.core.base_cst_transformer import BaseCstTransformer
from libcst_code_mods.core.base_cst_visitor import BaseCstVisitor
from libcst_code_mods.core.refactoring_rule import RefactoringRule
from libcst_code_mods.rules._rule_mapping import register_rule_transformer, register_rule_visitor

from ._replace_multiple_with_column_calls import update_multiple_with_column_calls


@attrs.define(frozen=True)
class ReplaceMultipleWithColumnRenamedCalls(RefactoringRule):
    pass


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
