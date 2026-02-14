from __future__ import annotations

from collections.abc import Callable

import libcst as cst
import libcst.matchers as m
from danom import Stream, compose

from libcst_code_mods.node_collector import NodeCollector
from libcst_code_mods.transformer import ApplyTransformations, NodeTransform


def apply_code_mod(  # noqa: PLR0913
    code: str,
    collecter_matcher: m.BaseMatcherNode,
    filter_fns: tuple[Callable[..., bool]],
    transform_fn: Callable[[cst.CSTNode], cst.CSTNode],
    transform_matcher: m.BaseMatcherNode | None = None,
    transform_matcher_fn: Callable[[cst.CSTNode], cst.CSTNode] | None = None,
) -> str:
    wrapper = cst.MetadataWrapper(code)
    collector = NodeCollector(collecter_matcher)
    wrapper.visit(collector)

    filtered = (
        Stream.from_iterable(collector.results).filter(compose(*filter_fns)).collect()
        if filter_fns
        else collector.results
    )
    replacements = {elem.node: NodeTransform(transform_fn) for elem in filtered}
    return wrapper.module.visit(
        ApplyTransformations(replacements, matcher=transform_matcher, transform_matcher_fn=transform_matcher_fn)
    ).code
