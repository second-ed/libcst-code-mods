from pathlib import Path

from libcst_code_mods.core.base_cst_visitor import BaseCstVisitor
from libcst_code_mods.core.cst_context import CstContext
from libcst_code_mods.engine import get_manager


def get_populated_visitor(root: str, visitor: BaseCstVisitor) -> BaseCstVisitor:
    paths = Path(root).rglob("**/*.py")

    manager = get_manager(str(root))
    context = CstContext({"root": Path(root)})

    visitor = visitor.from_context(context)

    for path in paths:
        wrapper = manager.get_metadata_wrapper_for_path(str(path))
        wrapper.visit(visitor)
    return visitor
