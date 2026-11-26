from collections.abc import Collection
from typing import ClassVar

import attrs
import libcst as cst
import libcst.matchers as m
from libcst.metadata import PositionProvider

from libcst_code_mods.core.base_cst_visitor import BaseCstVisitor
from libcst_code_mods.core.refactoring_rule import RefactoringRule
from libcst_code_mods.rules._rule_mapping import RULE_NAME_MAPPING, register_rule, register_rule_visitor


@register_rule
@attrs.frozen
class NoCollectInsideLoop(RefactoringRule):
    pass


COLLECT_IN_LOOP = m.FunctionDef(
    body=m.IndentedBlock(
        body=[
            m.ZeroOrMore(),
            m.SaveMatchedNode(
                m.For(
                    body=m.IndentedBlock(
                        body=[
                            m.ZeroOrMore(),
                            m.SimpleStatementLine(body=[m.Expr(m.Call(m.Attribute(attr=m.Name("collect"))))]),
                            m.ZeroOrMore(),
                        ]
                    )
                ),
                "loop",
            ),
            m.ZeroOrMore(),
        ]
    )
)


@register_rule_visitor(NoCollectInsideLoop)
@attrs.define
class NoCollectInsideLoopVisitor(BaseCstVisitor):
    METADATA_DEPENDENCIES: ClassVar[Collection[cst.metadata.ProviderT]] = (PositionProvider,)

    def visit_FunctionDef(self, node: cst.FunctionDef) -> bool | None:  # noqa: N802
        if (matched := m.extract(node, COLLECT_IN_LOOP)) is not None:
            loop = matched["loop"]
            self.add_diagnostic(
                loop, RULE_NAME_MAPPING[self.__class__], "build one distributed operation outside the loop"
            )
        return super().visit_FunctionDef(node)
