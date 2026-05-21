from __future__ import annotations

import attrs


@attrs.define(frozen=True)
class RefactoringRule:
    def to_dict(self) -> dict:
        return attrs.asdict(self)
