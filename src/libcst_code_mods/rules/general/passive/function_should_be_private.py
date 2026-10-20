from collections.abc import Collection
from typing import ClassVar

import attrs
import libcst as cst
from libcst.metadata import FullyQualifiedNameProvider, QualifiedNameSource

from libcst_code_mods.core.base_cst_transformer import BaseCstTransformer
from libcst_code_mods.core.base_cst_visitor import BaseCstVisitor
from libcst_code_mods.core.cst_context import CstContext
from libcst_code_mods.core.refactoring_rule import RefactoringRule
from libcst_code_mods.rules._rule_mapping import register_rule, register_rule_transformer, register_rule_visitor


@register_rule
@attrs.define(frozen=True)
class FunctionShouldBePrivate(RefactoringRule):
    """Examples:

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def public_function_used_by_another_module_stays_public(value: int) -> int:
                return private_function_only_used_within_module(1, 2)

        Post-transformer:

        .. code-block:: python

            def public_function_used_by_another_module_stays_public(value: int) -> int:
                return _private_function_only_used_within_module(1, 2)
    ---
    """

    ignore_function_names: tuple[str, ...] = attrs.field(factory=tuple, converter=tuple)


@register_rule_visitor(FunctionShouldBePrivate)
@attrs.define
class FunctionShouldBePrivateVisitor(BaseCstVisitor):
    METADATA_DEPENDENCIES: ClassVar[Collection[cst.metadata.ProviderT]] = (FullyQualifiedNameProvider,)

    ignore_function_names: tuple[str, ...]
    class_depth: int = 0
    function_depth: int = 0

    def visit_ClassDef(self, node: cst.ClassDef) -> bool:  # noqa: N802 ARG002
        self.class_depth += 1
        return True

    def leave_ClassDef(self, original_node: cst.ClassDef) -> None:  # noqa: N802 ARG002
        self.class_depth -= 1

    def visit_FunctionDef(self, node: cst.FunctionDef) -> bool:  # noqa: N802
        if not self.class_depth and not self.function_depth and node.name.value not in self.ignore_function_names:
            for qualified_name in self.get_metadata(FullyQualifiedNameProvider, node, set()):
                if qualified_name.source is not QualifiedNameSource.LOCAL:
                    continue

                self.context.paths.add(self.path)
                self.context.data.setdefault("function_definitions", {})[_canonical_name(qualified_name.name)] = (
                    node.name.value
                )

        self.function_depth += 1
        return True

    def leave_FunctionDef(self, original_node: cst.FunctionDef) -> None:  # noqa: N802 ARG002
        self.function_depth -= 1

    def visit_Call(self, node: cst.Call) -> bool:  # noqa: N802
        for qualified_name in self.get_metadata(FullyQualifiedNameProvider, node.func, set()):
            name = _canonical_name(qualified_name.name)
            if qualified_name.source is QualifiedNameSource.IMPORT:
                self.context.data.setdefault("imported_calls", set()).add(name)
            elif qualified_name.source is QualifiedNameSource.LOCAL:
                self.context.data.setdefault("local_calls", set()).add(name)

        return True

    @classmethod
    def finalize_context(cls, _rule: RefactoringRule, context: CstContext) -> list:
        definitions = context.data.get("function_definitions", {})
        local_calls = context.data.get("local_calls", set())
        imported_calls = context.data.get("imported_calls", set())
        context.data["private_function_names"] = frozenset(
            name
            for name, function_name in definitions.items()
            if not function_name.startswith("_") and name in local_calls and name not in imported_calls
        )
        return []


@register_rule_transformer(FunctionShouldBePrivate)
@attrs.define
class FunctionShouldBePrivateTransformer(BaseCstTransformer):
    METADATA_DEPENDENCIES: ClassVar[Collection[cst.metadata.ProviderT]] = (FullyQualifiedNameProvider,)

    private_function_names: frozenset[str] = attrs.field(factory=frozenset, converter=frozenset)

    def leave_Name(self, original_node: cst.Name, updated_node: cst.Name) -> cst.Name:  # noqa: N802
        if any(
            _canonical_name(qualified_name.name) in self.private_function_names
            and qualified_name.source is QualifiedNameSource.LOCAL
            for qualified_name in self.get_metadata(FullyQualifiedNameProvider, original_node, set())
        ):
            return updated_node.with_changes(value=f"_{updated_node.value}")

        return updated_node


def _canonical_name(name: str) -> str:
    return name.lstrip(".")
