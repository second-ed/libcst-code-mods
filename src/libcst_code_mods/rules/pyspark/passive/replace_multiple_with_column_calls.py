import attrs
import libcst as cst
import libcst.matchers as m

from libcst_code_mods.core.base_cst_transformer import BaseCstTransformer
from libcst_code_mods.core.refactoring_rule import RefactoringRule
from libcst_code_mods.rules._rule_mapping import register_rule_transformer


@attrs.define(frozen=True)
class ReplaceMultipleWithColumnCalls(RefactoringRule):
    pass


WITH_COLUMN_ATTR = m.Attribute(attr=m.Name("withColumn"))
WITH_COLUMN_CALL = m.Call(func=WITH_COLUMN_ATTR)


@register_rule_transformer(ReplaceMultipleWithColumnCalls)
@attrs.define
class ReplaceMultipleWithColumnCallsTransformer(BaseCstTransformer):
    def leave_Call(  # noqa: N802
        self, original_node: cst.Call, updated_node: cst.Call
    ) -> cst.BaseExpression:
        if not m.matches(updated_node, WITH_COLUMN_CALL):
            return updated_node

        parent = self.get_metadata(cst.metadata.ParentNodeProvider, original_node)

        # Only transform the outermost call in a chain.
        if m.matches(parent, WITH_COLUMN_ATTR):
            return updated_node

        columns = []
        current = updated_node

        while m.matches(current, WITH_COLUMN_CALL) and len(current.args) >= 2:  # noqa: PLR2004
            columns.append((current.args[0].value, current.args[1].value))
            current = current.func.value

        columns.reverse()

        return cst.Call(
            func=cst.Attribute(value=current, attr=cst.Name("withColumns")),
            args=[cst.Arg(value=cst.Dict(elements=[cst.DictElement(key=name, value=expr) for name, expr in columns]))],
        )
