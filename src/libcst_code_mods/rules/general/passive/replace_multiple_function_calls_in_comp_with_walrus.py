import attrs
import libcst as cst
import libcst.matchers as m

from libcst_code_mods.core.base_cst_transformer import BaseCstTransformer
from libcst_code_mods.core.base_cst_visitor import BaseCstVisitor
from libcst_code_mods.core.refactoring_rule import RefactoringRule
from libcst_code_mods.rules._rule_mapping import register_rule, register_rule_transformer, register_rule_visitor


@register_rule
@attrs.define(frozen=True)
class ReplaceMultipleFunctionCallsInCompWithWalrus(RefactoringRule):
    pass


LIST_COMP_MATCHER = m.ListComp(
    elt=m.SaveMatchedNode(m.Call(), "elt_call"),
    for_in=m.CompFor(ifs=[m.CompIf(test=m.SaveMatchedNode(m.Call(), "if_call"))]),
)


@register_rule_visitor(ReplaceMultipleFunctionCallsInCompWithWalrus)
@attrs.define
class ReplaceMultipleFunctionCallsInCompWithWalrusVisitor(BaseCstVisitor):
    def visit_ListComp(self, node: cst.ListComp) -> bool | None:  # noqa: N802
        if m.matches(node, LIST_COMP_MATCHER):
            self.context.paths.add(self.path)
        return super().visit_ListComp(node)


@register_rule_transformer(ReplaceMultipleFunctionCallsInCompWithWalrus)
@attrs.define
class ReplaceMultipleFunctionCallsInCompWithWalrusTransformer(BaseCstTransformer):
    def leave_ListComp(self, original_node: cst.ListComp, updated_node: cst.ListComp) -> cst.ListComp:  # noqa: N802
        extracted = m.extract(original_node, LIST_COMP_MATCHER)

        if extracted is None:
            return updated_node

        elt = extracted["elt_call"]
        cond = extracted["if_call"]

        tmp = cst.Name("__code_mod_tmp")
        walrus = cst.NamedExpr(target=tmp, value=elt, lpar=[cst.LeftParen()], rpar=[cst.RightParen()])
        new_cond = cond.visit(_ReplaceCallWithWalrus(call=elt, walrus=walrus))
        new_for = updated_node.for_in.with_changes(ifs=[cst.CompIf(test=new_cond)])

        return updated_node.with_changes(elt=tmp, for_in=new_for)


@attrs.define
class _ReplaceCallWithWalrus(cst.CSTTransformer):
    call: cst.Call
    walrus: cst.NamedExpr

    def leave_Call(self, original_node: cst.Call, updated_node: cst.Call) -> cst.Call | cst.NamedExpr:  # noqa: N802
        if original_node.deep_equals(self.call):
            return self.walrus
        return updated_node
