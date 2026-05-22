from __future__ import annotations

import attrs
import libcst as cst
import libcst.matchers as m

from libcst_code_mods.constants import METADATA_DEPS


class BaseMetadataTransformer(cst.CSTTransformer):
    METADATA_DEPENDENCIES = METADATA_DEPS


@attrs.define
class BaseAttrsTransformer(BaseMetadataTransformer):
    matcher: m.BaseMatcherNode | None

    def __call__(self, wrapper: cst.MetadataWrapper) -> cst.Module:
        return wrapper.visit(self)
