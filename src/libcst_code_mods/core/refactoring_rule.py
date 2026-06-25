from __future__ import annotations

from typing import Self

import attrs


@attrs.define(frozen=True)
class RefactoringRule:
    @classmethod
    def from_dict(cls, data: dict) -> Self:
        filtered = {f.name: data[f.name] for f in attrs.fields(cls) if f.name in data}
        return cls(**filtered)

    def to_dict(self) -> dict:
        return attrs.asdict(self)
