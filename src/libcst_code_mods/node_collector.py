import attrs
import libcst as cst
import libcst.matchers as m

from libcst_code_mods.constants import METADATA_DEPS


@attrs.define(frozen=True)
class NodeMetadata:
    node: cst.CSTNode = attrs.field(repr=False)
    position: cst.metadata.CodeRange
    scope: cst.metadata.Scope
    qualified_names: set[cst.metadata.QualifiedName]


class MetadataBase(cst.CSTVisitor):
    METADATA_DEPENDENCIES = METADATA_DEPS


@attrs.define
class NodeCollector(MetadataBase):
    matcher: m.BaseMatcherNode
    results: list[NodeMetadata] = attrs.field(factory=list)

    def on_visit(self, node: cst.CSTNode) -> bool:
        if not m.matches(node, self.matcher):
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
