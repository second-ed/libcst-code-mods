from __future__ import annotations

from typing import Any

import attrs


@attrs.define(frozen=True)
class CstContext:
    data: dict[str, Any] = attrs.field(factory=dict)
