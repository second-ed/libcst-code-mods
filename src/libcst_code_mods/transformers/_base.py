from __future__ import annotations

import attrs
import libcst as cst
import libcst.matchers as m

from libcst_code_mods.constants import METADATA_DEPS
from libcst_code_mods.node_collector import NodeMetadata


class BaseMetadataTransformer(cst.CSTTransformer):
    METADATA_DEPENDENCIES = METADATA_DEPS


@attrs.define
class BaseAttrsTransformer(BaseMetadataTransformer):
    collected_nodes: list[NodeMetadata] = attrs.field(init=False)
    matcher: m.BaseMatcherNode | None = attrs.field(init=False)
