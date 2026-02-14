from __future__ import annotations

from collections.abc import Callable

import attrs
import libcst as cst
import libcst.matchers as m


@attrs.define
class ApplyTransformations(cst.CSTTransformer):
    transform_map: dict[cst.CSTNode, Callable[[cst.CSTNode], cst.CSTNode]]
    matcher: m.BaseMatcherNode | None = attrs.field(default=None)
    transform_matcher_fn: Callable[[cst.CSTNode], cst.CSTNode] | None = attrs.field(default=None)

    def on_leave(self, original_node: cst.CSTNode, updated_node: cst.CSTNode) -> cst.CSTNode:
        if original_node in self.transform_map:
            transform = self.transform_map[original_node]
            return transform(updated_node)

        if self.matcher and self.transform_matcher_fn and m.matches(updated_node, self.matcher):
            return self.transform_matcher_fn(updated_node)

        return updated_node


@attrs.define(frozen=True)
class NodeTransform:
    transform_fn: Callable[[cst.CSTNode], cst.CSTNode]

    def __call__(self, updated_node: cst.CSTNode) -> cst.CSTNode:
        return self.transform_fn(updated_node)
