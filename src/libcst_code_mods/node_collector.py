# repo-map-desc: the pre-pass stage that collects the context before the transformation

from collections.abc import Collection
from typing import ClassVar

import attrs
import libcst as cst
import libcst.matchers as m


@attrs.define(frozen=True)
class NodeMetadata:
    node: cst.CSTNode = attrs.field(repr=False)
    position: cst.metadata.CodeRange
    scope: cst.metadata.Scope
    qualified_names: set[cst.metadata.QualifiedName]


@attrs.define
class NodeCollector(cst.CSTVisitor):
    METADATA_DEPENDENCIES: ClassVar[Collection[cst.metadata.ProviderT]] = (
        cst.metadata.PositionProvider,
        cst.metadata.ScopeProvider,
        cst.metadata.FullyQualifiedNameProvider,
    )

    matcher: m.BaseMatcherNode | None
    results: list[NodeMetadata] = attrs.field(factory=list)

    def on_visit(self, node: cst.CSTNode) -> bool:
        if self.matcher is not None and not m.matches(node, self.matcher):
            return True

        self.results.append(
            NodeMetadata(
                node=node,
                position=self.get_metadata(cst.metadata.PositionProvider, node, None),
                scope=self.get_metadata(cst.metadata.ScopeProvider, node, None),
                qualified_names=self.get_metadata(cst.metadata.FullyQualifiedNameProvider, node, set()),
            )
        )

        return True
