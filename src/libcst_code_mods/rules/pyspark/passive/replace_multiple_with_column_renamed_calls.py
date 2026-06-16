import attrs
import libcst as cst
import libcst.matchers as m

from libcst_code_mods.core.base_cst_transformer import BaseCstTransformer
from libcst_code_mods.core.refactoring_rule import RefactoringRule
from libcst_code_mods.rules._rule_mapping import register_rule_transformer

from ._replace_multiple_with_column_calls import update_multiple_with_column_calls


@attrs.define(frozen=True)
class ReplaceMultipleWithColumnRenamedCalls(RefactoringRule):
    pass


WITH_COLUMN_ATTR = m.Attribute(attr=m.Name("withColumnRenamed"))
WITH_COLUMN_CALL = m.Call(func=WITH_COLUMN_ATTR)


@register_rule_transformer(ReplaceMultipleWithColumnRenamedCalls)
@attrs.define
class ReplaceMultipleWithColumnRenamedCallsTransformer(BaseCstTransformer):
    def leave_Call(  # noqa: N802
        self, original_node: cst.Call, updated_node: cst.Call
    ) -> cst.BaseExpression:
        return update_multiple_with_column_calls(
            self, original_node, updated_node, WITH_COLUMN_CALL, WITH_COLUMN_ATTR, "withColumnsRenamed"
        )
