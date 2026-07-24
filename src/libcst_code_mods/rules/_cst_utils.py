import libcst as cst
import libcst.matchers as m

from libcst_code_mods.core.base_cst_transformer import BaseCstTransformer
from libcst_code_mods.core.base_cst_visitor import BaseCstVisitor


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


def extract_docstring_node_and_idx(
    node: cst.FunctionDef,
) -> tuple[tuple[cst.BaseStatement | cst.BaseSmallStatement] | tuple, int]:
    if has_docstring(node):
        return (node.body.body[0],), 1
    return (), 0


def has_docstring(node: cst.FunctionDef) -> bool:
    if not node.body.body:
        return False

    return m.matches(node.body.body[0], m.SimpleStatementLine([m.Expr(m.SimpleString())]))


def get_fqn(cls: BaseCstVisitor | BaseCstTransformer, node: cst.CSTNode) -> str | None:
    qualified_names = cls.get_metadata(cst.metadata.FullyQualifiedNameProvider, node, set())

    if not qualified_names:
        return None

    fqn = next(iter(qualified_names))

    if not isinstance(fqn, cst.metadata.QualifiedName):
        return None

    return fqn.name
