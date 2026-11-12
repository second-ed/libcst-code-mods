from collections.abc import Collection
from typing import ClassVar

import attrs
import libcst as cst
import libcst.matchers as m
from libcst.metadata import FunctionScope
from libcst.metadata.scope_provider import BuiltinAssignment

from libcst_code_mods.core.base_cst_transformer import BaseCstTransformer
from libcst_code_mods.core.base_cst_visitor import BaseCstVisitor
from libcst_code_mods.core.refactoring_rule import RefactoringRule
from libcst_code_mods.rules._cst_utils import get_fqn, prepend_comment_to_function
from libcst_code_mods.rules._rule_mapping import register_rule, register_rule_transformer, register_rule_visitor

PURE_BUILTIN_NAMES = frozenset(
    {
        "False",
        "MappingProxyType",
        "None",
        "True",
        "abs",
        "all",
        "any",
        "bool",
        "bytes",
        "dict",
        "enumerate",
        "filter",
        "float",
        "frozenset",
        "int",
        "isinstance",
        "iter",
        "len",
        "list",
        "map",
        "max",
        "min",
        "next",
        "object",
        "range",
        "set",
        "str",
        "sum",
        "tuple",
        "type",
        "zip",
    }
)
KNOWN_IMPURE_NAMES = frozenset({"open"})


@register_rule
@attrs.frozen
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

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def parse(value: str) -> int:
                return int(value)

        Post-transformer:

        .. code-block:: python

            def parse(value: str) -> int:
                # [[Likely pure]]
                return int(value)

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def size(value: str) -> int:
                return len(value)

        Post-transformer:

        .. code-block:: python

            def size(value: str) -> int:
                # [[Likely pure]]
                return len(value)

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def load(path: str) -> str:
                with open(path) as file:
                    return file.read()

        Post-transformer:

        .. code-block:: python

            def load(path: str) -> str:
                # [[Impure]]: Depends on [`open`] which is impure.
                with open(path) as file:
                    return file.read()

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def combined(value: str) -> int:
                return size(parse(value))

        Post-transformer:

        .. code-block:: python

            def combined(value: str) -> int:
                # [[Likely pure]]
                return size(parse(value))

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def main(path: str) -> None:
                data = load(path)
                combined(data)

        Post-transformer:

        .. code-block:: python

            def main(path: str) -> None:
                # [[Impure]]: Depends on [`load`] which is impure.
                data = load(path)
                combined(data)
    ---
    '''


@register_rule_visitor(IdentifyPureFunctions)
@attrs.define
class IdentifyPureFunctionsVisitor(BaseCstVisitor):
    METADATA_DEPENDENCIES: ClassVar[Collection[cst.metadata.ProviderT]] = (
        cst.metadata.ExpressionContextProvider,
        cst.metadata.ScopeProvider,
        cst.metadata.PositionProvider,
        cst.metadata.FullyQualifiedNameProvider,
    )

    function_dependencies: dict[str, list[str]] = attrs.field(factory=dict)
    function_names: dict[str, str] = attrs.field(factory=dict)

    def visit_FunctionDef(self, node: cst.FunctionDef) -> None:  # noqa: N802
        if (fqn := get_fqn(self, node)) is None:
            return

        self.function_names[node.name.value] = fqn
        dependencies = _function_dependencies(self, node)

        self.function_dependencies[fqn] = dependencies

        self.context.paths.add(self.path)
        self.context.data.setdefault("function_dependencies", {}).update(self.function_dependencies)
        self.context.data.setdefault("function_names", {}).update(self.function_names)


def _function_dependencies(visitor: IdentifyPureFunctionsVisitor, node: cst.FunctionDef) -> list[str]:
    parameter_names = {parameter.name.value for parameter in m.findall(node.params, m.Param(name=m.Name()))}
    dependencies = []
    for name in m.findall(node.body, m.Name()):
        dependency = _dependency_name(visitor, name, parameter_names)
        if dependency is not None and dependency not in dependencies:
            dependencies.append(dependency)
    return dependencies


def _dependency_name(visitor: IdentifyPureFunctionsVisitor, name: cst.Name, parameter_names: set[str]) -> str | None:
    if not _is_dependency_candidate(visitor, name, parameter_names):
        return None
    if (name_scope := visitor.get_metadata(cst.metadata.ScopeProvider, name, None)) is None:
        return None
    assignments = _assignments_for_name(name_scope, name)
    if _is_pure_builtin(name, assignments):
        return None
    return name.value if _possibly_impure_dependency([], name, name_scope, assignments) else None


def _is_dependency_candidate(visitor: IdentifyPureFunctionsVisitor, name: cst.Name, parameter_names: set[str]) -> bool:
    if name.value in parameter_names:
        return False
    return (
        visitor.get_metadata(cst.metadata.ExpressionContextProvider, name, None) is cst.metadata.ExpressionContext.LOAD
    )


def _assignments_for_name(name_scope: FunctionScope, name: cst.Name) -> set:
    return name_scope[name.value] if name.value in name_scope else set()  # noqa: SIM401


def _is_pure_builtin(name: cst.Name, assignments: set) -> bool:
    return name.value in PURE_BUILTIN_NAMES and all(
        assignment.__class__ is BuiltinAssignment for assignment in assignments
    )


@register_rule_transformer(IdentifyPureFunctions)
@attrs.define
class IdentifyPureFunctionsTransformer(BaseCstTransformer):
    METADATA_DEPENDENCIES: ClassVar[Collection[cst.metadata.ProviderT]] = (cst.metadata.FullyQualifiedNameProvider,)

    function_dependencies: dict[str, list[str]]
    function_names: dict[str, str]
    function_impurities: dict[str, list[str]] = attrs.field(init=False, factory=dict)

    def __attrs_post_init__(self) -> None:
        self.function_impurities = _classify_functions(self.function_dependencies, self.function_names)

    def leave_FunctionDef(  # noqa: N802
        self, original_node: cst.FunctionDef, updated_node: cst.FunctionDef
    ) -> cst.FunctionDef:
        if (fqn := get_fqn(self, original_node)) is None:
            return updated_node
        if (names := self.function_impurities.get(fqn)) is None:
            return _prepend_classification_comment(updated_node, "[[Likely pure]]")

        message = _format_impurity_message(names, self.function_names, set(self.function_impurities))
        return _prepend_classification_comment(updated_node, message)


def _classify_functions(
    function_dependencies: dict[str, list[str]], function_names: dict[str, str]
) -> dict[str, list[str]]:
    impurities = {
        fqn: [name for name in dependencies if name not in function_names]
        for fqn, dependencies in function_dependencies.items()
    }
    pure_functions = {fqn for fqn, dependencies in function_dependencies.items() if not dependencies}

    while new_functions := _new_pure_functions(function_dependencies, function_names, impurities, pure_functions):
        pure_functions = pure_functions | new_functions

    return {
        fqn: [
            name
            for name in dependencies
            if name in KNOWN_IMPURE_NAMES or name not in function_names or function_names[name] not in pure_functions
        ]
        for fqn, dependencies in function_dependencies.items()
        if fqn not in pure_functions
    }


def _new_pure_functions(
    function_dependencies: dict[str, list[str]],
    function_names: dict[str, str],
    impurities: dict[str, list[str]],
    pure_functions: set[str],
) -> set[str]:
    return {
        fqn
        for fqn, dependencies in function_dependencies.items()
        if fqn not in pure_functions and _is_pure(dependencies, function_names, impurities[fqn], pure_functions)
    }


def _is_pure(
    dependencies: list[str], function_names: dict[str, str], impurities: list[str], pure_functions: set[str]
) -> bool:
    called_functions = (function_names[name] for name in dependencies if name in function_names)
    return not impurities and all(name in pure_functions for name in called_functions)


def _possibly_impure_dependency(
    dependencies: list[str], name: cst.Name, name_scope: FunctionScope, assignments: set
) -> bool:
    return (
        (not assignments and name.value not in PURE_BUILTIN_NAMES)
        or any(assignment.scope is not name_scope for assignment in assignments)
    ) and name.value not in dependencies


def _format_impurity_message(
    dependencies: list[str], function_names: dict[str, str], impure_functions: set[str]
) -> str:
    if len(dependencies) == 1 and (
        dependencies[0] in KNOWN_IMPURE_NAMES or function_names.get(dependencies[0]) in impure_functions
    ):
        return f"[[Impure]]: Depends on [{_format_dependencies(dependencies)}] which is impure."

    return f"[[Impure]]: Depends on [{_format_dependencies(dependencies)}] which do not originate within this function."


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
    return formatted[0] if len(formatted) == 1 else ", ".join(formatted)
