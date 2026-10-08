from pathlib import Path

from libcst_code_mods.core.base_cst_visitor import BaseCstVisitor
from libcst_code_mods.core.cst_context import CstContext
from libcst_code_mods.engine import get_manager


def get_populated_visitor(root: str, visitor: BaseCstVisitor) -> BaseCstVisitor:
    cache = {}

    for path in Path(root).rglob("**/*.py"):
        wrapper = get_manager(str(root)).get_metadata_wrapper_for_path(str(path))
        cache = {**cache, **wrapper._cache}  # noqa: SLF001

        visitor = visitor.from_context(path, CstContext())
        wrapper.visit_batched([visitor])
    return visitor
