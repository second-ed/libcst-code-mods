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
    pass


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
