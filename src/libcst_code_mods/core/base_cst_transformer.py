from __future__ import annotations

from typing import Self

import attrs
import libcst as cst

from libcst_code_mods.constants import METADATA_DEPS
from libcst_code_mods.core.cst_context import CstContext


class BaseMetadataTransformer(cst.CSTTransformer):
    METADATA_DEPENDENCIES = METADATA_DEPS


@attrs.define
class BaseCstTransformer(BaseMetadataTransformer):
    @classmethod
    def from_context(cls, context: CstContext) -> Self:
        filtered = {f.name: context.data[f.name] for f in attrs.fields(cls) if f.name in context.data}
        return cls(**filtered)
