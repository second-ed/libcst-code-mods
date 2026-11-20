import libcst as cst
import libcst.matchers as m


def _is_true(expr: cst.BaseExpression) -> bool:
    return m.matches(expr, m.Name("True"))


def _is_false(expr: cst.BaseExpression) -> bool:
    return m.matches(expr, m.Name("False"))


def _is_not(expr: cst.BaseExpression, value: cst.BaseExpression) -> bool:
    return m.matches(expr, m.UnaryOperation(m.Not(), m.MatchIfTrue(lambda operand: operand.deep_equals(value))))


def _is_complement(left: cst.BaseExpression, right: cst.BaseExpression) -> bool:
    return _is_not(left, right) or _is_not(right, left)


def _flatten(expr: cst.BaseExpression, operator: m.BaseMatcherNode) -> list[cst.BaseExpression]:
    if m.matches(expr, m.BooleanOperation(operator=operator)):
        return _flatten(expr.left, operator) + _flatten(expr.right, operator)

    return [expr]


def _combine(expressions: list[cst.BaseExpression], operator: cst.BinaryOperation) -> cst.BaseExpression:
    result = expressions[0]

    for expression in expressions[1:]:
        result = cst.BooleanOperation(left=result, operator=operator, right=expression)

    return result


def _factor_complementary_terms(
    left: list[cst.BaseExpression], right: list[cst.BaseExpression], output_operator: cst.BinaryOperation
) -> cst.BaseExpression | None:
    remaining_left = list(left)
    remaining_right = list(right)
    common: list[cst.BaseExpression] = []

    for expression in left:
        if (
            matching_index := next(
                (index for index, candidate in enumerate(remaining_right) if expression.deep_equals(candidate)), None
            )
        ) is None:
            continue

        common.append(expression)
        remaining_left.remove(expression)
        remaining_right.pop(matching_index)

    if (
        len(remaining_left) != 1
        or len(remaining_right) != 1
        or not _is_complement(remaining_left[0], remaining_right[0])
    ):
        return None

    return _combine(common, output_operator)


def bool_identity_and(expr: cst.BooleanOperation) -> cst.BaseExpression:
    # A and True -> A
    if not m.matches(expr.operator, m.And()):
        return expr

    if _is_true(expr.right):
        return expr.left

    if _is_true(expr.left):
        return expr.right

    return expr


def bool_identity_or(expr: cst.BooleanOperation) -> cst.BaseExpression:
    # A or False -> A
    if not m.matches(expr.operator, m.Or()):
        return expr

    if _is_false(expr.right):
        return expr.left

    if _is_false(expr.left):
        return expr.right

    return expr


def bool_domination_and(expr: cst.BooleanOperation) -> cst.BaseExpression:
    # A and False -> False
    if not m.matches(expr.operator, m.And()):
        return expr

    if _is_false(expr.left) or _is_false(expr.right):
        return cst.Name("False")

    return expr


def bool_domination_or(expr: cst.BooleanOperation) -> cst.BaseExpression:
    # A or True -> True
    if not m.matches(expr.operator, m.Or()):
        return expr

    if _is_true(expr.left) or _is_true(expr.right):
        return cst.Name("True")

    return expr


def bool_idempotent_and(expr: cst.BooleanOperation) -> cst.BaseExpression:
    # A and A -> A
    if m.matches(expr.operator, m.And()) and expr.left.deep_equals(expr.right):
        return expr.left

    return expr


def bool_idempotent_or(expr: cst.BooleanOperation) -> cst.BaseExpression:
    # A or A -> A
    if m.matches(expr.operator, m.Or()) and expr.left.deep_equals(expr.right):
        return expr.left

    return expr


def bool_complement_and(expr: cst.BooleanOperation) -> cst.BaseExpression:
    # A and not A -> False
    if not m.matches(expr.operator, m.And()):
        return expr

    if _is_not(expr.left, expr.right) or _is_not(expr.right, expr.left):
        return cst.Name("False")

    return expr


def bool_complement_or(expr: cst.BooleanOperation) -> cst.BaseExpression:
    # A or not A -> True
    if not m.matches(expr.operator, m.Or()):
        return expr

    if _is_not(expr.left, expr.right) or _is_not(expr.right, expr.left):
        return cst.Name("True")

    return expr


def bool_double_negation(expr: cst.UnaryOperation) -> cst.BaseExpression:
    # not not A -> A
    if not m.matches(expr.operator, m.Not()):
        return expr

    inner = expr.expression

    if m.matches(inner, m.UnaryOperation(m.Not())):
        return inner.expression

    return expr


def bool_constant_negation(expr: cst.UnaryOperation) -> cst.BaseExpression:
    # not True -> False
    if not m.matches(expr.operator, m.Not()):
        return expr

    if _is_true(expr.expression):
        return cst.Name("False")

    if _is_false(expr.expression):
        return cst.Name("True")

    return expr


def _not_expression(expr: cst.BaseExpression) -> cst.UnaryOperation:
    return cst.UnaryOperation(operator=cst.Not(), expression=expr)


def bool_demorgan(expr: cst.UnaryOperation) -> cst.BaseExpression:
    # not (A and B) -> not A or not B
    # not (A or B) -> not A and not B
    if not m.matches(expr.operator, m.Not()):
        return expr

    inner = expr.expression

    if m.matches(inner, m.BooleanOperation(operator=m.And())):
        return cst.BooleanOperation(
            left=_not_expression(inner.left), operator=cst.Or(), right=_not_expression(inner.right)
        )

    if m.matches(inner, m.BooleanOperation(operator=m.Or())):
        return cst.BooleanOperation(
            left=_not_expression(inner.left), operator=cst.And(), right=_not_expression(inner.right)
        )

    return expr


def bool_absorption_or(expr: cst.BooleanOperation) -> cst.BaseExpression:
    # A or (A and B) -> A
    if not m.matches(expr.operator, m.Or()):
        return expr

    for first, second in ((expr.left, expr.right), (expr.right, expr.left)):
        if m.matches(second, m.BooleanOperation(operator=m.And())) and (
            first.deep_equals(second.left) or first.deep_equals(second.right)
        ):
            return first

    return expr


def bool_absorption_and(expr: cst.BooleanOperation) -> cst.BaseExpression:
    # A and (A or B) -> A
    if not m.matches(expr.operator, m.And()):
        return expr

    for first, second in ((expr.left, expr.right), (expr.right, expr.left)):
        if m.matches(second, m.BooleanOperation(operator=m.Or())) and (
            first.deep_equals(second.left) or first.deep_equals(second.right)
        ):
            return first

    return expr


def bool_factor_and_or(expr: cst.BooleanOperation) -> cst.BaseExpression:
    # (A and B) or (A and not B) -> A
    if not m.matches(expr.operator, m.Or()):
        return expr

    factored = _factor_complementary_terms(_flatten(expr.left, m.And()), _flatten(expr.right, m.And()), cst.And())
    return factored if factored is not None else expr


def bool_factor_or_and(expr: cst.BooleanOperation) -> cst.BaseExpression:
    # (A or B) and (A or not B) -> A
    if not m.matches(expr.operator, m.And()):
        return expr

    factored = _factor_complementary_terms(_flatten(expr.left, m.Or()), _flatten(expr.right, m.Or()), cst.Or())
    return factored if factored is not None else expr


BASIC_BOOLEAN_RULES = (
    bool_identity_and,
    bool_identity_or,
    bool_domination_and,
    bool_domination_or,
    bool_idempotent_and,
    bool_idempotent_or,
    bool_complement_and,
    bool_complement_or,
    bool_absorption_and,
    bool_absorption_or,
)


COMPOSITE_BOOLEAN_RULES = (bool_factor_and_or, bool_factor_or_and)


UNARY_BOOLEAN_RULES = (bool_constant_negation, bool_double_negation, bool_demorgan)
