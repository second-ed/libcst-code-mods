from __future__ import annotations

from collections.abc import Callable, Sequence

import attrs
import libcst as cst
import libcst.matchers as m

from libcst_code_mods.node_collector import NodeCollector, NodeMetadata
from libcst_code_mods.transformer import ApplyTransformations, NodeTransform


def apply_code_mod(  # noqa: PLR0913
    code: str,
    collecter_matcher: m.BaseMatcherNode,
    filter_fns: Sequence[Callable[[NodeMetadata], bool]],
    transform_fn: Callable[[cst.CSTNode], cst.CSTNode],
    transform_matcher: m.BaseMatcherNode | None = None,
    transform_matcher_fn: Callable[[cst.CSTNode], cst.CSTNode] | None = None,
) -> str:
    wrapper = cst.MetadataWrapper(cst.parse_module(code))
    collector = NodeCollector(collecter_matcher)
    wrapper.visit(collector)

    if filter_fns:
        all_of = AllOf(filter_fns)
        filtered = [res for res in collector.results if all_of(res)]
    else:
        filtered = collector.results

    replacements = {elem.node: NodeTransform(transform_fn) for elem in filtered}
    transformer = ApplyTransformations(
        replacements, matcher=transform_matcher, transform_matcher_fn=transform_matcher_fn
    )
    return wrapper.module.visit(transformer).code


@attrs.define(frozen=True, hash=True, eq=True)
class AllOf:
    fns: Sequence[Callable[[NodeMetadata], bool]]

    def __call__(self, item: NodeMetadata) -> bool:
        return all(fn(item) for fn in self.fns)
