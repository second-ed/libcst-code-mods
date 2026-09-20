from collections.abc import Sequence

import attrs
import libcst as cst
import libcst.matchers as m

from libcst_code_mods.core.base_cst_transformer import BaseCstTransformer
from libcst_code_mods.core.base_cst_visitor import BaseCstVisitor
from libcst_code_mods.core.refactoring_rule import RefactoringRule
from libcst_code_mods.rules._cst_utils import extract_docstring_node_and_idx, get_fqn, normalise
from libcst_code_mods.rules._rule_mapping import register_rule, register_rule_transformer, register_rule_visitor


@register_rule
@attrs.define(frozen=True)
class ReplaceMutableDefaultsWithGuardClause(RefactoringRule):
    '''Examples:

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def func(a: int, b: list[int] = []) -> list[int]:
                """some docstring"""
                x = 1
                b.extend([a, x])
                return b

        Post-transformer:

        .. code-block:: python

            def func(a: int, b: list[int] | None = None) -> list[int]:
                """some docstring"""
                b = b if b is not None else []
                x = 1
                b.extend([a, x])
                return b

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def func_2(a: int, b: dict = {}) -> None:
                pass

        Post-transformer:

        .. code-block:: python

            def func_2(a: int, b: dict | None = None) -> None:
                b = b if b is not None else {}
                pass

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def func_3(a: int, b: set = set()) -> None:
                pass

        Post-transformer:

        .. code-block:: python

            def func_3(a: int, b: set | None = None) -> None:
                b = b if b is not None else set()
                pass

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def func_4(a: int, b: list = list()) -> None:
                pass

        Post-transformer:

        .. code-block:: python

            def func_4(a: int, b: list | None = None) -> None:
                b = b if b is not None else []
                pass

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def kw_only_mutable_default(a: dict = {}, /, *, b: list[int] = []) -> None:
                pass

        Post-transformer:

        .. code-block:: python

            def kw_only_mutable_default(a: dict | None = None, /, *, b: list[int] | None = None) -> None:
                a = a if a is not None else {}
                b = b if b is not None else []
                pass

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def big_func(a: int, b: list = [], c: dict = {}, d: set = set(), e: list = list(), f: dict = dict()) -> None:
                pass

        Post-transformer:

        .. code-block:: python

            def big_func(
                a: int,
                b: list | None = None,
                c: dict | None = None,
                d: set | None = None,
                e: list | None = None,
                f: dict | None = None,
            ) -> None:
                b = b if b is not None else []
                c = c if c is not None else {}
                d = d if d is not None else set()
                e = e if e is not None else []
                f = f if f is not None else {}
                pass
    ---
    '''


MUTABLE_DEFAULT = m.OneOf(
    m.List(), m.Dict(), m.Set(), m.Call(m.Name("list")), m.Call(m.Name("set")), m.Call(m.Name("dict"))
)


@register_rule_visitor(ReplaceMutableDefaultsWithGuardClause)
@attrs.define
class ReplaceMutableDefaultsWithGuardClauseVisitor(BaseCstVisitor):
    mutable_params: dict[str, dict[str, str]] = attrs.field(factory=dict)
    mutable_pos_only_params: dict[str, dict[str, str]] = attrs.field(factory=dict)
    mutable_kw_only_params: dict[str, dict[str, str]] = attrs.field(factory=dict)

    def visit_FunctionDef(self, node: cst.FunctionDef) -> None:  # noqa: N802

        if (fqn := get_fqn(self, node)) is None:
            return

        config = (
            (node.params.params, self.mutable_params),
            (node.params.posonly_params, self.mutable_pos_only_params),
            (node.params.kwonly_params, self.mutable_kw_only_params),
        )
        for params, param_dict in config:
            _add_params(params, param_dict, fqn)

        if self.mutable_params or self.mutable_pos_only_params or self.mutable_kw_only_params:
            self.context.paths.add(self.path)

            context_config = (
                ("mutable_params", self.mutable_params),
                ("mutable_pos_only_params", self.mutable_pos_only_params),
                ("mutable_kw_only_params", self.mutable_kw_only_params),
            )
            for key, values in context_config:
                self.context.data.setdefault(key, {}).update(values)


def _add_params(params: Sequence[cst.Param], param_dict: dict[str, dict[str, str]], fqn: str) -> None:
    for param in params:
        if param.default is not None and m.matches(param.default, MUTABLE_DEFAULT):
            param_dict.setdefault(fqn, {})[param.name.value] = normalise(param.default)


REPLACEMENTS: dict[str, cst.BaseExpression] = {
    "[]": cst.List([]),
    "{}": cst.Dict([]),
    "set()": cst.Call(cst.Name("set")),
    "list()": cst.List([]),
    "dict()": cst.Dict([]),
}


@register_rule_transformer(ReplaceMutableDefaultsWithGuardClause)
@attrs.define
class ReplaceMutableDefaultsWithGuardClauseTransformer(BaseCstTransformer):
    mutable_params: dict[str, dict[str, str]]
    mutable_pos_only_params: dict[str, dict[str, str]]
    mutable_kw_only_params: dict[str, dict[str, str]]

    def leave_FunctionDef(self, original_node: cst.FunctionDef, updated_node: cst.FunctionDef) -> cst.FunctionDef:  # noqa: N802
        fqn = get_fqn(self, original_node)

        if fqn is None or not any(
            fqn in params for params in (self.mutable_params, self.mutable_pos_only_params, self.mutable_kw_only_params)
        ):
            return updated_node

        all_params = {
            **self.mutable_params.get(fqn, {}),
            **self.mutable_pos_only_params.get(fqn, {}),
            **self.mutable_kw_only_params.get(fqn, {}),
        }

        guards = [_make_guard(name, default) for name, default in all_params.items()]

        docstring_nodes, slice_idx = extract_docstring_node_and_idx(updated_node)
        new_body = [*docstring_nodes, *guards, *updated_node.body.body[slice_idx:]]

        params = _update_params(updated_node.params.params, self.mutable_params.get(fqn, {}))
        pos_only_params = _update_params(updated_node.params.posonly_params, self.mutable_pos_only_params.get(fqn, {}))
        kw_only_params = _update_params(updated_node.params.kwonly_params, self.mutable_kw_only_params.get(fqn, {}))

        return updated_node.with_changes(
            params=updated_node.params.with_changes(
                params=params, kwonly_params=kw_only_params, posonly_params=pos_only_params
            ),
            body=updated_node.body.with_changes(body=new_body),
        )


def _update_params(params: Sequence[cst.Param], fn_param_map: dict[str, str]) -> list[cst.Param]:
    new_params = []

    for param in params:
        if fn_param_map.get(param.name.value) is None:
            new_params.append(param)
            continue

        if (annotation := param.annotation) is not None:
            annotation = cst.Annotation(
                cst.BinaryOperation(left=annotation.annotation, operator=cst.BitOr(), right=cst.Name("None"))
            )

        new_params.append(param.with_changes(default=cst.Name("None"), annotation=annotation))
    return new_params


def _make_guard(name: str, default: str) -> cst.SimpleStatementLine:
    return cst.SimpleStatementLine(
        body=[
            cst.Assign(
                targets=[cst.AssignTarget(target=cst.Name(name))],
                value=cst.IfExp(
                    test=cst.Comparison(
                        left=cst.Name(name),
                        comparisons=[cst.ComparisonTarget(operator=cst.IsNot(), comparator=cst.Name("None"))],
                    ),
                    body=cst.Name(name),
                    # perf hack, use or short circuiting to only do the expensive parsing when the default falls through
                    orelse=REPLACEMENTS.get(default) or cst.parse_expression(default),
                ),
            )
        ]
    )
