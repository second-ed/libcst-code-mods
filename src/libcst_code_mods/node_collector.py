import attrs
import libcst as cst
import libcst.matchers as m


@attrs.define(frozen=True)
class NodeMetadata:
    node: cst.CSTNode = attrs.field(repr=False)
    position: cst.metadata.CodeRange
    scope: cst.metadata.Scope
    qualified_names: set[cst.metadata.QualifiedName]


class MetadataBase(cst.CSTVisitor):
    METADATA_DEPENDENCIES = (
        cst.metadata.PositionProvider,
        cst.metadata.ScopeProvider,
        cst.metadata.QualifiedNameProvider,
    )


@attrs.define
class NodeCollector(MetadataBase):
    matcher: m.BaseMatcherNode
    results: list = attrs.field(factory=list)

    def on_visit(self, node: cst.CSTNode) -> bool:
        if not m.matches(node, self.matcher):
            return True

        self.results.append(
            NodeMetadata(
                node=node,
                position=self.get_metadata(cst.metadata.PositionProvider, node, None),
                scope=self.get_metadata(cst.metadata.ScopeProvider, node, None),
                qualified_names=self.get_metadata(cst.metadata.QualifiedNameProvider, node, set()),
            )
        )

        return True
