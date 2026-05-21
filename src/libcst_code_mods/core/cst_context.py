from __future__ import annotations

import attrs


@attrs.define(frozen=True)
class CstContext:
    data: dict[str, object] = attrs.field(factory=dict)
