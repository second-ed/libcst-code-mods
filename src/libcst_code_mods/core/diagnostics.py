from pathlib import Path

import attrs
from libcst.metadata import CodeRange


@attrs.define(frozen=True)
class Diagnostic:
    rule: str
    path: Path
    code_range: CodeRange
    code: str
    instead: str | None = None

    def to_dict(self) -> dict[str, str | int]:
        diagnostic = {
            "rule": self.rule,
            "path": str(self.path),
            "start_line": self.code_range.start.line,
            "start_col": self.code_range.start.column,
            "end_line": self.code_range.end.line,
            "end_col": self.code_range.end.column,
            "code": self.code.strip("\n"),
        }
        if self.instead:
            diagnostic["instead"] = self.instead
        return diagnostic


def relative_path(path: Path, root: Path) -> Path:
    return path.resolve().relative_to(root)
