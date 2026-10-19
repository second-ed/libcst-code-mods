from __future__ import annotations

from collections.abc import Collection
from pathlib import Path
from typing import ClassVar, Self

import attrs
import libcst as cst

from libcst_code_mods.core.cst_context import CstContext
from libcst_code_mods.core.diagnostics import Diagnostic, relative_path
from libcst_code_mods.core.refactoring_rule import RefactoringRule


class BaseMetadataVisitor(cst.BatchableCSTVisitor):
    METADATA_DEPENDENCIES: ClassVar[Collection[cst.metadata.ProviderT]] = ()


@attrs.define
class BaseCstVisitor(BaseMetadataVisitor):
    path: str
    context: CstContext

    def add_diagnostic(self, node: cst.CSTNode, rule: str, instead: str) -> None:
        self.context.paths.add(self.path)
        self.context.diagnostics.add(
            Diagnostic(
                rule=rule,
                path=relative_path(Path(self.path), self.context.root),
                code_range=self.get_metadata(cst.metadata.PositionProvider, node),
                code=cst.Module([]).code_for_node(node),
                instead=instead,
            )
        )

    @classmethod
    def from_context(cls, path: str, context: CstContext) -> Self:
        filtered = {f.name: context.data[f.name] for f in attrs.fields(cls) if f.name in context.data}
        return cls(path=path, context=context, **filtered)

    @classmethod
    def finalize_context(cls, _rule: RefactoringRule, _context: CstContext) -> list:
        return []
