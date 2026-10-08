from __future__ import annotations

from pathlib import Path
from typing import Any

import attrs

from libcst_code_mods.core.diagnostics import Diagnostic


@attrs.define(frozen=True)
class CstContext:
    root: Path
    paths: set[str] = attrs.field(factory=set)
    data: dict[str, Any] = attrs.field(factory=dict)
    diagnostics: set[Diagnostic] = attrs.field(factory=set)
