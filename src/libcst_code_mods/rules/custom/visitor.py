from fnmatch import fnmatchcase
from pathlib import Path

import attrs
import libcst as cst
import libcst.matchers as m

from libcst_code_mods.core.base_cst_visitor import BaseCstVisitor


@attrs.define
class CustomDiagnosticVisitor(BaseCstVisitor):
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

    def on_visit(self, node: cst.CSTNode) -> bool:
        if self.path_enabled and m.matches(node, self.matcher):
            self.add_diagnostic(node, self.rule, self.instead)
        return True


def _path_is_enabled(path: str, root: Path, include: tuple[str, ...], exclude: tuple[str, ...]) -> bool:
    relative_path = Path(path).resolve().relative_to(root).as_posix()

    included = not include or any(fnmatchcase(relative_path, pattern) for pattern in include)
    excluded = any(fnmatchcase(relative_path, pattern) for pattern in exclude)

    return included and not excluded
