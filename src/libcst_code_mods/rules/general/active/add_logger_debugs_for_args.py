import attrs
import libcst as cst

from libcst_code_mods.core.base_cst_transformer import BaseCstTransformer
from libcst_code_mods.core.base_cst_visitor import BaseCstVisitor
from libcst_code_mods.core.refactoring_rule import RefactoringRule
from libcst_code_mods.rules._cst_utils import extract_docstring_node_and_idx
from libcst_code_mods.rules._rule_mapping import register_rule, register_rule_transformer, register_rule_visitor


@register_rule
@attrs.define(frozen=True)
class AddLoggerDebugsForArgs(RefactoringRule):
    '''Examples:

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def func(a: int, b: str, c: float) -> str:
                """some random docstring"""
                if a % 2 == 0:
                    return b + str(c)
                return str(c)

        Post-transformer:

        .. code-block:: python

            def func(a: int, b: str, c: float) -> str:
                """some random docstring"""
                logger.debug(f"{a = } {b = } {c = } ")
                if a % 2 == 0:
                    return b + str(c)
                return str(c)

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def new_sum(value_1: int, value_2: int) -> int:
                return value_1 + value_2

        Post-transformer:

        .. code-block:: python

            def new_sum(value_1: int, value_2: int) -> int:
                logger.debug(f"{value_1 = } {value_2 = } ")
                return value_1 + value_2
    ---
    '''

    fn_names: list[str]


@register_rule_visitor(AddLoggerDebugsForArgs)
@attrs.define
class AddLoggerDebugsForArgsVisitor(BaseCstVisitor):
    fn_names: list[str]

    def visit_FunctionDef(self, node: cst.FunctionDef) -> None:  # noqa: N802
        if node.name.value not in self.fn_names:
            return
        param_types = self.context.data.setdefault("param_names", {})
        param_types[node.name.value] = [p.name.value for p in node.params.params]
        self.context.paths.add(self.path)


@register_rule_transformer(AddLoggerDebugsForArgs)
@attrs.define
class AddLoggerDebugsForArgsTransformer(BaseCstTransformer):
    fn_names: list[str]
    param_names: dict[str, list[str]]

    def leave_FunctionDef(self, original_node: cst.FunctionDef, updated_node: cst.FunctionDef) -> cst.FunctionDef:  # noqa: N802 ARG002
        if (
            updated_node.name.value not in self.fn_names
            or (fn_params := self.param_names.get(updated_node.name.value)) is None
        ):
            return updated_node

        msg_parts = ['f"']
        msg_parts.extend(f"{{{param} = }} " for param in fn_params)
        msg_parts.append('"')

        msg = "".join(msg_parts)
        debugs = cst.parse_statement(f"logger.debug({msg})")

        docstring_nodes, slice_idx = extract_docstring_node_and_idx(updated_node)

        return updated_node.with_changes(
            body=updated_node.body.with_changes(body=[*docstring_nodes, debugs, *updated_node.body.body[slice_idx:]])
        )
