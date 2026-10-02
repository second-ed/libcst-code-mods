from pathlib import Path

import attrs
from libcst.metadata import CodeRange


@attrs.define(frozen=True)
class Diagnostic:
    path: str
    code_range: CodeRange
    code: str

    def to_str(self) -> str:
        range_str = f"[{self.code_range.start.line}:{self.code_range.start.column}-{self.code_range.end.line}:{self.code_range.end.column}]"

        return f"{self.path}{range_str}: {self.code}"


def relative_path(path: str, root: Path) -> str:
    return str(Path(path).resolve().relative_to(root))
