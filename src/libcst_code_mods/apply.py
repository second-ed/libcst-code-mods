from __future__ import annotations

from collections.abc import Callable, Sequence
from pathlib import Path

import attrs
import libcst as cst
import libcst.matchers as m
from libcst.metadata import FullRepoManager

from libcst_code_mods.constants import METADATA_DEPS
from libcst_code_mods.node_collector import NodeCollector, NodeMetadata


def apply_code_mod(
    root: str,
    path: str,
    collecter_matcher: m.BaseMatcherNode,
    transformer: cst.CSTTransformer,
    filter_fns: Sequence[Callable[[NodeMetadata], bool]] | None = None,
) -> str:
    wrapper = get_manager(root).get_metadata_wrapper_for_path(path)
    collector = NodeCollector(collecter_matcher)
    wrapper.visit(collector)

    if filter_fns:
        all_of = AllOf(filter_fns)
        filtered = [res for res in collector.results if all_of(res)]
    else:
        filtered = collector.results

    transformer.collected_nodes = filtered
    return wrapper.module.visit(transformer).code


def get_manager(root: str) -> FullRepoManager:
    return FullRepoManager(root, paths=list(map(str, Path(root).rglob("**/*.py"))), providers=METADATA_DEPS)


@attrs.define(frozen=True, hash=True, eq=True)
class AllOf:
    fns: Sequence[Callable[[NodeMetadata], bool]]

    def __call__(self, item: NodeMetadata) -> bool:
        return all(fn(item) for fn in self.fns)
