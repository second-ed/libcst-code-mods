from collections.abc import Collection
from pathlib import Path
from typing import ClassVar

import attrs
import libcst as cst
import libcst.matchers as m

from libcst_code_mods.core.base_cst_transformer import BaseCstTransformer
from libcst_code_mods.core.base_cst_visitor import BaseCstVisitor
from libcst_code_mods.core.diagnostics import Diagnostic, relative_path
from libcst_code_mods.core.refactoring_rule import RefactoringRule
from libcst_code_mods.rules._cst_utils import normalise
from libcst_code_mods.rules._rule_mapping import (
    RULE_NAME_MAPPING,
    register_rule,
    register_rule_transformer,
    register_rule_visitor,
)
from libcst_code_mods.rules.testing.passive._utils import in_test


@register_rule
@attrs.define(frozen=True)
class NoAssertsInLoop(RefactoringRule):
    pass


ASSERTS_IN_LOOP = m.FunctionDef(
    body=m.IndentedBlock(
        body=[
            m.ZeroOrMore(),
            m.SaveMatchedNode(
                m.For(
                    body=m.IndentedBlock(
                        body=[m.ZeroOrMore(), m.SimpleStatementLine(body=[m.Assert()]), m.ZeroOrMore()]
                    )
                ),
                "loop",
            ),
            m.ZeroOrMore(),
        ]
    )
)


@register_rule_visitor(NoAssertsInLoop)
@attrs.define
class NoAssertsInLoopVisitor(BaseCstVisitor):
    METADATA_DEPENDENCIES: ClassVar[Collection[cst.metadata.ProviderT]] = (cst.metadata.PositionProvider,)

    def visit_FunctionDef(self, node: cst.FunctionDef) -> bool | None:  # noqa: N802
        if in_test(self.path, node) and (matched := m.extract(node, ASSERTS_IN_LOOP)) is not None:
            loop = matched["loop"]
            self.context.paths.add(self.path)
            self.context.diagnostics.add(
                Diagnostic(
                    rule=RULE_NAME_MAPPING[self.__class__],
                    path=relative_path(Path(self.path), self.context.root),
                    code_range=self.get_metadata(cst.metadata.PositionProvider, loop),
                    code=normalise(loop),
                    instead="assert once against the entire iterable",
                )
            )
        return super().visit_FunctionDef(node)


@register_rule_transformer(NoAssertsInLoop)
@attrs.define
class NoAssertsInLoopTransformer(BaseCstTransformer):
    pass
