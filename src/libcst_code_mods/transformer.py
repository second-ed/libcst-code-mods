from collections.abc import Callable

import attrs
import libcst as cst


@attrs.define
class ApplyTransformations(cst.CSTTransformer):
    transform_map: dict[cst.CSTNode, Callable[[cst.CSTNode], cst.CSTNode]]

    def on_leave(self, original_node: cst.CSTNode, updated_node: cst.CSTNode) -> cst.CSTNode:
        if original_node not in self.transform_map:
            return updated_node

        transform = self.transform_map[original_node]
        return transform(updated_node)


@attrs.define(frozen=True)
class NodeTransform:
    transform_fn: Callable[[cst.CSTNode], cst.CSTNode]

    def __call__(self, updated_node: cst.CSTNode) -> cst.CSTNode:
        return self.transform_fn(updated_node)
