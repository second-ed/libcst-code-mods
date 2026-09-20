import attrs
import libcst as cst
import libcst.matchers as m

from libcst_code_mods.core.base_cst_transformer import BaseCstTransformer
from libcst_code_mods.core.base_cst_visitor import BaseCstVisitor
from libcst_code_mods.core.refactoring_rule import RefactoringRule
from libcst_code_mods.rules._rule_mapping import register_rule, register_rule_transformer, register_rule_visitor


@register_rule
@attrs.define(frozen=True)
class ReplaceNestedListCompsWithLinearGenExps(RefactoringRule):
    """Examples:

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def nested_comps_with_depth_1(y: list) -> None:
                z = [fn_1(a) for a in y]

        Post-transformer:

        .. code-block:: python

            def nested_comps_with_depth_1(y: list) -> None:
                z = list(map(fn_1, y))

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def nested_comps_with_depth_1_and_filters_1(y: list) -> None:
                z = [fn_1(a) for a in y if fil_1(a)]

        Post-transformer:

        .. code-block:: python

            def nested_comps_with_depth_1_and_filters_1(y: list) -> None:
                __s = filter(fil_1, y)
                z = list(map(fn_1, __s))

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def nested_comps_with_depth_2(y: list) -> None:
                z = (fn_2(b) for b in (fn_1(a) for a in y))

        Post-transformer:

        .. code-block:: python

            def nested_comps_with_depth_2(y: list) -> None:
                __s = map(fn_1, y)
                z = map(fn_2, __s)

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def nested_comps_with_depth_2_and_filters_1(y: list) -> None:
                z = [fn_2(b) for b in [fn_1(a) for a in y if fil_1(a)]]

        Post-transformer:

        .. code-block:: python

            def nested_comps_with_depth_2_and_filters_1(y: list) -> None:
                __s = filter(fil_1, y)
                __s = map(fn_1, __s)
                z = list(map(fn_2, __s))

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def nested_comps_with_depth_2_and_filters_2(y: list) -> None:
                z = [fn_2(b) for b in [fn_1(a) for a in y if fil_1(a)] if fil_2(b)]

        Post-transformer:

        .. code-block:: python

            def nested_comps_with_depth_2_and_filters_2(y: list) -> None:
                __s = filter(fil_1, y)
                __s = map(fn_1, __s)
                __s = filter(fil_2, __s)
                z = list(map(fn_2, __s))

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def nested_comps_with_depth_3(y: list) -> None:
                z = [fn_3(c) for c in [fn_2(b) for b in [fn_1(a) for a in y]]]

        Post-transformer:

        .. code-block:: python

            def nested_comps_with_depth_3(y: list) -> None:
                __s = map(fn_1, y)
                __s = map(fn_2, __s)
                z = list(map(fn_3, __s))

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def nested_comps_with_depth_3_and_filters_1(y: list) -> None:
                z = [fn_3(c) for c in [fn_2(b) for b in [fn_1(a) for a in y if fil_1(a)]]]

        Post-transformer:

        .. code-block:: python

            def nested_comps_with_depth_3_and_filters_1(y: list) -> None:
                __s = filter(fil_1, y)
                __s = map(fn_1, __s)
                __s = map(fn_2, __s)
                z = list(map(fn_3, __s))

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def nested_comps_with_depth_3_and_filters_2(y: list) -> None:
                z = [fn_3(c) for c in [fn_2(b) for b in [fn_1(a) for a in y if fil_1(a)] if fil_2(b)]]

        Post-transformer:

        .. code-block:: python

            def nested_comps_with_depth_3_and_filters_2(y: list) -> None:
                __s = filter(fil_1, y)
                __s = map(fn_1, __s)
                __s = filter(fil_2, __s)
                __s = map(fn_2, __s)
                z = list(map(fn_3, __s))

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def nested_comps_with_depth_3_and_filters_3(y: list) -> None:
                z = [fn_3(c) for c in [fn_2(b) for b in [fn_1(a) for a in y if fil_1(a)] if fil_2(b)] if fil_3(c)]

        Post-transformer:

        .. code-block:: python

            def nested_comps_with_depth_3_and_filters_3(y: list) -> None:
                __s = filter(fil_1, y)
                __s = map(fn_1, __s)
                __s = filter(fil_2, __s)
                __s = map(fn_2, __s)
                __s = filter(fil_3, __s)
                z = list(map(fn_3, __s))

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def nested_comps_with_depth_4(y: list) -> None:
                z = [fn_4(d) for d in [fn_3(c) for c in [fn_2(b) for b in [fn_1(a) for a in y]]]]

        Post-transformer:

        .. code-block:: python

            def nested_comps_with_depth_4(y: list) -> None:
                __s = map(fn_1, y)
                __s = map(fn_2, __s)
                __s = map(fn_3, __s)
                z = list(map(fn_4, __s))

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def nested_comps_with_depth_4_and_filters_1(y: list) -> None:
                z = [fn_4(d) for d in [fn_3(c) for c in [fn_2(b) for b in [fn_1(a) for a in y if fil_1(a)]]]]

        Post-transformer:

        .. code-block:: python

            def nested_comps_with_depth_4_and_filters_1(y: list) -> None:
                __s = filter(fil_1, y)
                __s = map(fn_1, __s)
                __s = map(fn_2, __s)
                __s = map(fn_3, __s)
                z = list(map(fn_4, __s))

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def nested_comps_with_depth_4_and_filters_2(y: list) -> None:
                z = [fn_4(d) for d in [fn_3(c) for c in [fn_2(b) for b in [fn_1(a) for a in y if fil_1(a)] if fil_2(b)]]]

        Post-transformer:

        .. code-block:: python

            def nested_comps_with_depth_4_and_filters_2(y: list) -> None:
                __s = filter(fil_1, y)
                __s = map(fn_1, __s)
                __s = filter(fil_2, __s)
                __s = map(fn_2, __s)
                __s = map(fn_3, __s)
                z = list(map(fn_4, __s))

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def nested_comps_with_depth_4_and_filters_3(y: list) -> list:
                return [
                    fn_4(d) for d in [fn_3(c) for c in [fn_2(b) for b in [fn_1(a) for a in y if fil_1(a)] if fil_2(b)] if fil_3(c)]
                ]

        Post-transformer:

        .. code-block:: python

            def nested_comps_with_depth_4_and_filters_3(y: list) -> list:
                __s = filter(fil_1, y)
                __s = map(fn_1, __s)
                __s = filter(fil_2, __s)
                __s = map(fn_2, __s)
                __s = filter(fil_3, __s)
                __s = map(fn_3, __s)
                return list(map(fn_4, __s))

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def nested_comps_with_depth_4_and_filters_4(y: list) -> None:
                z = [
                    fn_4(d)
                    for d in [fn_3(c) for c in [fn_2(b) for b in [fn_1(a) for a in y if fil_1(a)] if fil_2(b)] if fil_3(c)]
                    if fil_4(d)
                ]

        Post-transformer:

        .. code-block:: python

            def nested_comps_with_depth_4_and_filters_4(y: list) -> None:
                __s = filter(fil_1, y)
                __s = map(fn_1, __s)
                __s = filter(fil_2, __s)
                __s = map(fn_2, __s)
                __s = filter(fil_3, __s)
                __s = map(fn_3, __s)
                __s = filter(fil_4, __s)
                z = list(map(fn_4, __s))

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def nested_comps_with_multiple_fn_calls(y: list) -> None:
                z = [fn_2(fn_1(a)) for a in y if fil_2(fil_1(a))]

        Post-transformer:

        .. code-block:: python

            def nested_comps_with_multiple_fn_calls(y: list) -> None:
                __s = filter(fil_1, y)
                __s = filter(fil_2, __s)
                __s = map(fn_1, __s)
                z = list(map(fn_2, __s))
    ---
    """


COMPREHENSION_MATCHER = m.OneOf(m.ListComp(), m.GeneratorExp())
COMPREHENSION_PARTS_MATCHER = m.OneOf(
    m.ListComp(elt=m.DoNotCare(), for_in=m.CompFor(target=m.Name(), inner_for_in=None)),
    m.GeneratorExp(elt=m.DoNotCare(), for_in=m.CompFor(target=m.Name(), inner_for_in=None)),
)
CALL_MATCHER = m.Call(args=[m.Arg(keyword=None, star="", value=m.DoNotCare())])
COMPREHENSION_STATEMENT_MATCHER = m.SimpleStatementLine(
    body=[m.OneOf(m.Assign(value=COMPREHENSION_MATCHER), m.Return(value=COMPREHENSION_MATCHER))]
)


@register_rule_visitor(ReplaceNestedListCompsWithLinearGenExps)
@attrs.define
class ReplaceNestedListCompsWithLinearGenExpsVisitor(BaseCstVisitor):
    def visit_SimpleStatementLine(self, node: cst.SimpleStatementLine) -> None:  # noqa: N802
        if m.matches(node, COMPREHENSION_STATEMENT_MATCHER):
            self.context.paths.add(self.path)


@register_rule_transformer(ReplaceNestedListCompsWithLinearGenExps)
@attrs.define
class ReplaceNestedListCompsWithLinearGenExpsTransformer(BaseCstTransformer):
    def leave_SimpleStatementLine(  # noqa: N802
        self, original_node: cst.SimpleStatementLine, updated_node: cst.SimpleStatementLine
    ) -> cst.SimpleStatementLine | cst.FlattenSentinel[cst.SimpleStatementLine]:
        if not m.matches(original_node, COMPREHENSION_STATEMENT_MATCHER):
            return updated_node

        if (pipeline := _build_pipeline(original_node.body[0].value)) is None:
            return updated_node

        stream, operations, output_as_list = pipeline
        assignments, stream = _build_stream_assignments(stream, operations[:-1])
        result = _call(operations[-1][0], operations[-1][1], stream)
        if output_as_list:
            result = _list_call(result)

        result_line = updated_node.with_changes(body=[updated_node.body[0].with_changes(value=result)])
        return cst.FlattenSentinel([*assignments, result_line])


def _build_pipeline(
    value: cst.BaseExpression,
) -> tuple[cst.BaseExpression, list[tuple[str, cst.BaseExpression]], bool] | None:
    if not (comprehensions := _collect_comprehensions(value)):
        return None

    source, comprehensions = comprehensions
    if not (operations := _build_operations(comprehensions)):
        return None
    return source, operations, m.matches(value, m.ListComp())


def _collect_comprehensions(
    value: cst.BaseExpression,
) -> tuple[cst.BaseExpression, list[tuple[list[cst.BaseExpression], cst.CompFor]]] | None:
    comprehensions: list[tuple[list[cst.BaseExpression], cst.CompFor]] = []
    current = value

    while m.matches(current, COMPREHENSION_MATCHER):
        if (parts := _get_comprehension_parts(current)) is None:
            return None
        comprehensions.append(parts)
        comp_for = parts[1]
        current = comp_for.iter

    if not comprehensions:
        return None
    return current, comprehensions


def _get_comprehension_parts(
    node: cst.ListComp | cst.GeneratorExp,
) -> tuple[list[cst.BaseExpression], cst.CompFor] | None:
    if not m.matches(node, COMPREHENSION_PARTS_MATCHER):
        return None
    comp_for = node.for_in
    if (functions := _call_chain(node.elt, comp_for.target)) is None:
        return None
    return functions, comp_for


def _build_operations(
    comprehensions: list[tuple[list[cst.BaseExpression], cst.CompFor]],
) -> list[tuple[str, cst.BaseExpression]] | None:
    operations: list[tuple[str, cst.BaseExpression]] = []
    for functions, comp_for in reversed(comprehensions):
        if (filter_functions := _get_filter_functions(comp_for)) is None:
            return None
        operations.extend(("filter", function) for function in filter_functions)
        operations.extend(("map", function) for function in functions)
    return operations


def _get_filter_functions(comp_for: cst.CompFor) -> list[cst.BaseExpression] | None:
    functions: list[cst.BaseExpression] = []
    for comp_if in comp_for.ifs:
        if (chain := _call_chain(comp_if.test, comp_for.target)) is None:
            return None
        functions.extend(chain)
    return functions


def _call_chain(expression: cst.BaseExpression, target: cst.Name) -> list[cst.BaseExpression] | None:
    functions: list[cst.BaseExpression] = []
    while m.matches(expression, CALL_MATCHER):
        functions.append(expression.func)
        expression = expression.args[0].value
    if not expression.deep_equals(target):
        return None
    return list(reversed(functions))


def _build_stream_assignments(
    stream: cst.BaseExpression, operations: list[tuple[str, cst.BaseExpression]]
) -> tuple[list[cst.SimpleStatementLine], cst.BaseExpression]:
    assignments: list[cst.SimpleStatementLine] = []
    for operation, function in operations:
        stream = _call(operation, function, stream)
        assignments.append(_assignment("__s", stream))
        stream = cst.Name("__s")
    return assignments, stream


def _call(name: str, function: cst.BaseExpression, argument: cst.BaseExpression) -> cst.Call:
    return cst.Call(func=cst.Name(name), args=[cst.Arg(value=function), cst.Arg(value=argument)])


def _list_call(argument: cst.BaseExpression) -> cst.Call:
    return cst.Call(func=cst.Name("list"), args=[cst.Arg(value=argument)])


def _assignment(name: str, value: cst.BaseExpression) -> cst.SimpleStatementLine:
    return cst.SimpleStatementLine(body=[cst.Assign(targets=[cst.AssignTarget(target=cst.Name(name))], value=value)])
