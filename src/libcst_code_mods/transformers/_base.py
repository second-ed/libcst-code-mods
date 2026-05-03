from __future__ import annotations

import attrs
import libcst as cst

from libcst_code_mods.node_collector import NodeMetadata


@attrs.define
class BaseMetadataTransformer(cst.CSTTransformer):
    collected_nodes: list[NodeMetadata] = attrs.field(init=False)
