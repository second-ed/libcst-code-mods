from collections.abc import Callable

import libcst as cst
import libcst.matchers as m
from danom import Stream, compose

from libcst_code_mods.node_collector import NodeCollector
from libcst_code_mods.transformer import ApplyTransformations, NodeTransform


def apply_code_mod(
    code: str,
    matcher: m.BaseMatcherNode,
    filter_fns: tuple[Callable[..., bool]],
    transform_fn: Callable[[cst.CSTNode], cst.CSTNode],
) -> str:
    wrapper = cst.MetadataWrapper(code)
    collector = NodeCollector(matcher)
    wrapper.visit(collector)

    filtered = (
        Stream.from_iterable(collector.results).filter(compose(*filter_fns)).collect()
        if filter_fns
        else collector.results
    )
    replacements = {elem.node: NodeTransform(transform_fn) for elem in filtered}
    return wrapper.module.visit(ApplyTransformations(replacements)).code
