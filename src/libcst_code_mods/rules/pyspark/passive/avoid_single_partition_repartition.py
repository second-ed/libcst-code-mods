from collections.abc import Collection
from typing import ClassVar

import attrs
import libcst as cst
import libcst.matchers as m

from libcst_code_mods.core.base_cst_visitor import BaseCstVisitor
from libcst_code_mods.core.refactoring_rule import RefactoringRule
from libcst_code_mods.rules._cst_utils import is_part_of_call_chain
from libcst_code_mods.rules._rule_mapping import RULE_NAME_MAPPING, register_rule, register_rule_visitor


@register_rule
@attrs.define(frozen=True)
class AvoidSinglePartitionRepartition(RefactoringRule):
    pass


SINGLE_PARTITION_CALL = m.Call(
    func=m.Attribute(attr=m.OneOf(m.Name("repartition"), m.Name("coalesce"))),
    args=[m.Arg(value=m.Integer(value="1"), keyword=None)],
)


@register_rule_visitor(AvoidSinglePartitionRepartition)
@attrs.define
class AvoidSinglePartitionRepartitionVisitor(BaseCstVisitor):
    METADATA_DEPENDENCIES: ClassVar[Collection[cst.metadata.ProviderT]] = (
        cst.metadata.ParentNodeProvider,
        cst.metadata.PositionProvider,
    )

    def visit_Call(self, node: cst.Call) -> bool | None:  # noqa: N802
        if _contains_single_partition_call(node) and not is_part_of_call_chain(self, node):
            self.add_diagnostic(
                node,
                RULE_NAME_MAPPING[self.__class__],
                "This call forces 1 output partition. Remove it or use a partition count that matches the workload.",
            )
        return super().visit_Call(node)


def _contains_single_partition_call(node: cst.Call) -> bool:
    return bool(m.findall(node, SINGLE_PARTITION_CALL))
