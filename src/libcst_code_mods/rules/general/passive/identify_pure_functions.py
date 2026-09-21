import attrs
import libcst as cst
import libcst.matchers as m

from libcst_code_mods.core.base_cst_transformer import BaseCstTransformer
from libcst_code_mods.core.base_cst_visitor import BaseCstVisitor
from libcst_code_mods.core.refactoring_rule import RefactoringRule
from libcst_code_mods.rules._cst_utils import get_fqn, prepend_comment_to_function
from libcst_code_mods.rules._rule_mapping import register_rule, register_rule_transformer, register_rule_visitor

TWO_DEPENDENCIES = 2


@register_rule
@attrs.define(frozen=True)
class IdentifyPureFunctions(RefactoringRule):
    '''Examples:

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def a_fn_that_only_depends_on_its_args(a: int, b: int) -> int:
                res = a + b
                return res

        Post-transformer:

        .. code-block:: python

            def a_fn_that_only_depends_on_its_args(a: int, b: int) -> int:
                # [[Likely pure]]
                res = a + b
                return res

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def a_fn_that_depends_on_a_non_local_variable(a: int, b: int) -> int:
                res = a + b + C
                return res

        Post-transformer:

        .. code-block:: python

            def a_fn_that_depends_on_a_non_local_variable(a: int, b: int) -> int:
                # [[Impure]]: Depends on [`C`] which do not originate within this function.
                res = a + b + C
                return res

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def an_impure_fn_with_an_existing_docstring(a: int, b: int) -> int:
                """This function has an existing docstring

                Args:
                    a (int): the first parameter
                    b (int): the second parameter

                Returns:
                    int: the sum of the 2 args
                """
                registry[a] = b
                registry[b] = C
                return a + b

        Post-transformer:

        .. code-block:: python

            def an_impure_fn_with_an_existing_docstring(a: int, b: int) -> int:
                # [[Impure]]: Depends on [`registry`, `C`] which do not originate within this function.
                """This function has an existing docstring

                Args:
                    a (int): the first parameter
                    b (int): the second parameter

                Returns:
                    int: the sum of the 2 args
                """
                registry[a] = b
                registry[b] = C
                return a + b
    ---
    '''


@register_rule_visitor(IdentifyPureFunctions)
@attrs.define
class IdentifyPureFunctionsVisitor(BaseCstVisitor):
    function_dependencies: dict[str, list[str]] = attrs.field(factory=dict)

    def visit_FunctionDef(self, node: cst.FunctionDef) -> None:  # noqa: N802
        if (fqn := get_fqn(self, node)) is None:
            return

        dependencies = []
        for name in m.findall(node.body, m.Name()):
            if (
                self.get_metadata(cst.metadata.ExpressionContextProvider, name)
                is not cst.metadata.ExpressionContext.LOAD
            ):
                continue

            name_scope = self.get_metadata(cst.metadata.ScopeProvider, name)
            assignments = name_scope[name.value] if name.value in name_scope else set()  # noqa: SIM401
            if (
                not assignments or any(assignment.scope is not name_scope for assignment in assignments)
            ) and name.value not in dependencies:
                dependencies.append(name.value)

        if dependencies:
            self.function_dependencies[fqn] = dependencies

        self.context.paths.add(self.path)
        self.context.data.setdefault("function_dependencies", {}).update(self.function_dependencies)


@register_rule_transformer(IdentifyPureFunctions)
@attrs.define
class IdentifyPureFunctionsTransformer(BaseCstTransformer):
    function_dependencies: dict[str, list[str]]

    def leave_FunctionDef(  # noqa: N802
        self, original_node: cst.FunctionDef, updated_node: cst.FunctionDef
    ) -> cst.FunctionDef:
        if (fqn := get_fqn(self, original_node)) is None:
            return updated_node
        if (names := self.function_dependencies.get(fqn)) is None:
            return _prepend_classification_comment(updated_node, "[[Likely pure]]")

        message = f"[[Impure]]: Depends on [{_format_dependencies(names)}] which do not originate within this function."
        return _prepend_classification_comment(updated_node, message)


def _prepend_classification_comment(node: cst.FunctionDef, text: str) -> cst.FunctionDef:
    first_statement = node.body.body[0]
    classification_lines = [
        (
            line.with_changes(comment=cst.Comment(f"# {text}"))
            if m.matches(line, m.EmptyLine(comment=m.Comment())) and line.comment.value.startswith("# [[")
            else line
        )
        for line in first_statement.leading_lines
    ]
    if any(
        m.matches(line, m.EmptyLine(comment=m.Comment())) and line.comment.value.startswith("# [[")
        for line in first_statement.leading_lines
    ):
        return node.with_changes(
            body=node.body.with_changes(
                body=[first_statement.with_changes(leading_lines=classification_lines), *node.body.body[1:]]
            )
        )

    return prepend_comment_to_function(node, text)


def _format_dependencies(dependencies: list[str]) -> str:
    formatted = [f"`{dependency}`" for dependency in dependencies]
    if len(formatted) == 1:
        return formatted[0]
    return ", ".join(formatted)
