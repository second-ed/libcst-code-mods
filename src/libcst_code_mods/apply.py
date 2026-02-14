from __future__ import annotations

from collections.abc import Callable, Sequence

import attrs
import libcst as cst
import libcst.matchers as m

from libcst_code_mods.node_collector import NodeCollector, NodeMetadata


def apply_code_mod(code: str, collecter_matcher: m.BaseMatcherNode, transformer: cst.CSTTransformer) -> str:
    wrapper = cst.MetadataWrapper(cst.parse_module(code))
    collector = NodeCollector(collecter_matcher)
    wrapper.visit(collector)
    return wrapper.module.visit(transformer).code


@attrs.define(frozen=True, hash=True, eq=True)
class AllOf:
    fns: Sequence[Callable[[NodeMetadata], bool]]

    def __call__(self, item: NodeMetadata) -> bool:
        return all(fn(item) for fn in self.fns)
