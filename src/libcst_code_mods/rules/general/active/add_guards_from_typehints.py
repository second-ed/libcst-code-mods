import attrs
import libcst as cst
import libcst.matchers as m

from libcst_code_mods.core.base_cst_transformer import BaseCstTransformer
from libcst_code_mods.core.base_cst_visitor import BaseCstVisitor
from libcst_code_mods.core.refactoring_rule import RefactoringRule
from libcst_code_mods.rules._cst_utils import extract_docstring_node_and_idx
from libcst_code_mods.rules._rule_mapping import register_rule, register_rule_transformer, register_rule_visitor


@register_rule
@attrs.define(frozen=True)
class AddGuardsFromTypehints(RefactoringRule):
    '''Examples:

        Case:

        Pre-transformer:

        .. code-block:: python

            def func(a: int, b: str, c: float) -> str:
                """some test multi line docstring

                Args:
                    a (int): _description_
                    b (str): _description_
                    c (float): _description_

                Returns:
                    str: _description_
                """
                if a % 2 == 0:
                    return b + str(c)
                return str(c)

        Post-transformer:

        .. code-block:: python

            def func(a: int, b: str, c: float) -> str:
                """some test multi line docstring

                Args:
                    a (int): _description_
                    b (str): _description_
                    c (float): _description_

                Returns:
                    str: _description_
                """
                if not all([isinstance(a, int), isinstance(b, str), isinstance(c, float)]):
                    raise TypeError(
                        f"Invalid arg types:\n`a` expected `int` got `{type(a)}`\n`b` expected `str` got `{type(b)}`\n`c` expected `float` got `{type(c)}`"
                    )
                if a % 2 == 0:
                    return b + str(c)
                return str(c)


        Case:

        Pre-transformer:

        .. code-block:: python

            def add(a: int, b: int) -> int:
                return a + b

        Post-transformer:

        .. code-block:: python

            def add(a: int, b: int) -> int:
                if not all([isinstance(a, int), isinstance(b, int)]):
                    raise TypeError(
                        f"Invalid arg types:\n`a` expected `int` got `{type(a)}`\n`b` expected `int` got `{type(b)}`"
                    )
                return a + b


        Case:

        Pre-transformer:

        .. code-block:: python

            def big_func(a: int, b: list[str], c: dict[int, str], d: set[float]) -> None:
                pass

        Post-transformer:

        .. code-block:: python

            def big_func(a: int, b: list[str], c: dict[int, str], d: set[float]) -> None:
                if not all([isinstance(a, int), isinstance(b, list), isinstance(c, dict), isinstance(d, set)]):
                    raise TypeError(
                        f"Invalid arg types:\n`a` expected `int` got `{type(a)}`\n`b` expected `list` got `{type(b)}`\n`c` expected `dict` got `{type(c)}`\n`d` expected `set` got `{type(d)}`"
                    )
                pass
    ::
    '''

    fn_names: list[str]


@register_rule_visitor(AddGuardsFromTypehints)
@attrs.define
class AddGuardsFromTypehintsVisitor(BaseCstVisitor):
    fn_names: list[str]

    def visit_FunctionDef(self, node: cst.FunctionDef) -> None:  # noqa: N802
        if node.name.value not in self.fn_names:
            return
        param_types = self.context.data.setdefault("param_types", {})
        param_types[node.name.value] = {
            p.name.value: _extract_type_hint(p.annotation.annotation)
            for p in node.params.params
            if p.annotation is not None
        }
        self.context.paths.add(self.path)


def _extract_type_hint(annotation: cst.Annotation) -> str | None:
    if isinstance(annotation, cst.Name):
        return annotation.value

    if m.matches(annotation, m.Subscript(m.Name())):
        return annotation.value.value
    return None


@register_rule_transformer(AddGuardsFromTypehints)
@attrs.define
class AddGuardsFromTypehintsTransformer(BaseCstTransformer):
    fn_names: list[str]
    param_types: dict[str, dict[str, str]]

    def leave_FunctionDef(self, original_node: cst.FunctionDef, updated_node: cst.FunctionDef) -> cst.FunctionDef:  # noqa: N802 ARG002
        if (
            updated_node.name.value not in self.fn_names
            or (fn_param_map := self.param_types.get(updated_node.name.value)) is None
        ):
            return updated_node

        isinstance_checks, type_err_expected = [], []

        for param, annot in fn_param_map.items():
            isinstance_checks.append(f"isinstance({param}, {annot})")
            type_err_expected.append(f"`{param}` expected `{annot}` got `{{type({param})}}`")

        msg = "Invalid arg types:\\n" + "\\n".join(type_err_expected)
        isinstance_checks_str = ", ".join(isinstance_checks)

        guards = cst.parse_statement(f"if not all([{isinstance_checks_str}]): raise TypeError(f'{msg}')")

        docstring_nodes, slice_idx = extract_docstring_node_and_idx(updated_node)

        return updated_node.with_changes(
            body=updated_node.body.with_changes(body=[*docstring_nodes, guards, *updated_node.body.body[slice_idx:]])
        )
