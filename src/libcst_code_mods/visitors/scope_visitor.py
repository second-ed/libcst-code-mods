from enum import StrEnum, unique
from pathlib import Path

import attrs
import libcst as cst

from libcst_code_mods.core.base_cst_visitor import BaseCstVisitor


@unique
class ScopeType(StrEnum):
    MODULE = "module"
    CLASS = "class"
    FN = "fn"
    LISTCOMP = "listcomp"
    SETCOMP = "setcomp"
    DICTCOMP = "dictcomp"
    GENEXP = "genexp"


@attrs.define(frozen=True)
class ScopeFrame:
    kind: ScopeType
    name: str


@attrs.define
class ScopeVisitor(BaseCstVisitor):
    root: Path
    _file_path: str | None = None
    _scope_stack: list[ScopeFrame] = attrs.field(factory=list)

    def visit_Module(self, node: cst.Module) -> bool | None:  # noqa: N802
        self._file_path = self.get_metadata(cst.metadata.FilePathProvider, node, "FAILED_TO_GET_FILEPATH")
        module_name = str(self._file_path.relative_to(self.root)).replace("/", ".").removesuffix(".py")
        self._record_scope(kind=ScopeType.MODULE, name=module_name)
        return super().visit_Module(node)

    def leave_Module(self, original_node: cst.Module) -> None:  # noqa: N802
        self._scope_stack.pop()
        self._file_path = None
        return super().leave_Module(original_node)

    def visit_ClassDef(self, node: cst.ClassDef) -> bool | None:  # noqa: N802
        self._record_scope(kind=ScopeType.CLASS, name=node.name.value)
        return super().visit_ClassDef(node)

    def leave_ClassDef(self, original_node: cst.ClassDef) -> None:  # noqa: N802
        self._scope_stack.pop()
        return super().leave_ClassDef(original_node)

    def visit_FunctionDef(self, node: cst.FunctionDef) -> bool | None:  # noqa: N802
        self._record_scope(kind=ScopeType.FN, name=node.name.value)
        return super().visit_FunctionDef(node)

    def leave_FunctionDef(self, original_node: cst.FunctionDef) -> None:  # noqa: N802
        self._scope_stack.pop()
        return super().leave_FunctionDef(original_node)

    def visit_ListComp(self, node: cst.ListComp) -> bool | None:  # noqa: N802
        self._record_scope(kind=ScopeType.LISTCOMP, name="<listcomp>")
        return super().visit_ListComp(node)

    def leave_ListComp(self, original_node: cst.ListComp) -> None:  # noqa: N802
        self._scope_stack.pop()
        return super().leave_ListComp(original_node)

    def visit_SetComp(self, node: cst.SetComp) -> bool | None:  # noqa: N802
        self._record_scope(kind=ScopeType.SETCOMP, name="<setcomp>")
        return super().visit_SetComp(node)

    def leave_SetComp(self, original_node: cst.SetComp) -> None:  # noqa: N802
        self._scope_stack.pop()
        return super().leave_SetComp(original_node)

    def visit_DictComp(self, node: cst.DictComp) -> bool | None:  # noqa: N802
        self._record_scope(kind=ScopeType.DICTCOMP, name="<dictcomp>")
        return super().visit_DictComp(node)

    def leave_DictComp(self, original_node: cst.DictComp) -> None:  # noqa: N802
        self._scope_stack.pop()
        return super().leave_DictComp(original_node)

    def visit_GeneratorExp(self, node: cst.GeneratorExp) -> bool | None:  # noqa: N802
        self._record_scope(kind=ScopeType.GENEXP, name="<genexp>")
        return super().visit_GeneratorExp(node)

    def leave_GeneratorExp(self, original_node: cst.GeneratorExp) -> None:  # noqa: N802
        self._scope_stack.pop()
        return super().leave_GeneratorExp(original_node)

    def _record_scope(self, kind: ScopeType, name: str) -> None:
        self._scope_stack.append(ScopeFrame(kind=kind, name=name))
        self.context.data[self.current_scope] = {"file": self._file_path}

    @property
    def current_scope(self) -> str:
        return ".".join(frame.name for frame in self._scope_stack) if self._scope_stack else "<module>"
