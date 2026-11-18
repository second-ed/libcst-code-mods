from collections.abc import Callable, Collection
from fnmatch import fnmatchcase
from pathlib import Path
from types import MethodType
from typing import ClassVar, Self

import attrs
import libcst as cst
import libcst.matchers as m
from libcst.metadata import PositionProvider

from libcst_code_mods.core.base_cst_visitor import BaseCstVisitor
from libcst_code_mods.core.cst_context import CstContext


@attrs.define(slots=False)
class CustomDiagnosticVisitor(BaseCstVisitor):
    METADATA_DEPENDENCIES: ClassVar[Collection[cst.metadata.ProviderT]] = (PositionProvider,)

    rule: str
    matcher: m.BaseMatcherNode
    instead: str
    include: tuple[str, ...] = ()
    exclude: tuple[str, ...] = ()
    path_enabled: bool = attrs.field(default=False)

    def __attrs_post_init__(self) -> None:
        self.path_enabled = _path_is_enabled(
            path=self.path, root=self.context.root, include=self.include, exclude=self.exclude
        )

    @classmethod
    def new(  # noqa: PLR0913
        cls,
        path: str,
        context: CstContext,
        rule: str,
        matcher: m.BaseMatcherNode,
        instead: str,
        include: tuple[str, ...],
        exclude: tuple[str, ...],
        matcher_name: str,
    ) -> Self:
        instance = cls(path, context, rule=rule, matcher=matcher, instead=instead, include=include, exclude=exclude)
        method_name = f"visit_{matcher_name}"
        method = _make_visit_method(method_name)
        setattr(instance, method_name, MethodType(method, instance))
        return instance


def _path_is_enabled(path: str, root: Path, include: tuple[str, ...], exclude: tuple[str, ...]) -> bool:
    relative_path = Path(path).resolve().relative_to(root).as_posix()

    included = not include or any(fnmatchcase(relative_path, pattern) for pattern in include)
    excluded = any(fnmatchcase(relative_path, pattern) for pattern in exclude)

    return included and not excluded


def _make_visit_method(method_name: str) -> Callable[[CustomDiagnosticVisitor, cst.CSTNode], bool]:
    def on_visit(self: CustomDiagnosticVisitor, node: cst.CSTNode) -> bool:
        if self.path_enabled and m.matches(node, self.matcher):
            self.add_diagnostic(node, self.rule, self.instead)
        return True

    on_visit.__name__ = method_name
    return on_visit
