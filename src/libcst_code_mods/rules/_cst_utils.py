import libcst as cst
import libcst.matchers as m


def normalise(node: cst.CSTNode | None) -> str:
    return cst.Module([]).code_for_node(node)


def invert_condition(expr: cst.BaseExpression) -> cst.BaseExpression:
    if m.matches(expr, m.UnaryOperation(m.Not())):
        return expr.expression

    if m.matches(expr, m.Comparison()):
        return invert_comparison(expr)

    return cst.UnaryOperation(operator=cst.Not(), expression=expr)


COMPARISON_INVERSES = {
    cst.Equal: cst.NotEqual,
    cst.NotEqual: cst.Equal,
    cst.Is: cst.IsNot,
    cst.IsNot: cst.Is,
    cst.In: cst.NotIn,
    cst.NotIn: cst.In,
}


def invert_comparison(expr: cst.Comparison) -> cst.BaseExpression:
    if len(expr.comparisons) != 1:
        return cst.UnaryOperation(operator=cst.Not(), expression=expr)

    target = expr.comparisons[0]
    inverse = COMPARISON_INVERSES.get(type(target.operator))

    if inverse is None:
        return cst.UnaryOperation(operator=cst.Not(), expression=expr)

    return expr.with_changes(comparisons=[target.with_changes(operator=inverse())])
