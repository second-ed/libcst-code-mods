import attrs
import libcst as cst
import libcst.matchers as m

from libcst_code_mods.core.base_cst_transformer import BaseCstTransformer
from libcst_code_mods.core.base_cst_visitor import BaseCstVisitor
from libcst_code_mods.core.diagnostics import Diagnostic, relative_path
from libcst_code_mods.core.refactoring_rule import RefactoringRule
from libcst_code_mods.rules._cst_utils import normalise
from libcst_code_mods.rules._rule_mapping import register_rule, register_rule_transformer, register_rule_visitor


def in_test(path: str, node: cst.FunctionDef) -> bool:
    return path.rsplit("/", maxsplit=1)[-1].startswith("test_") and node.name.value.startswith("test_")


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
    def visit_FunctionDef(self, node: cst.FunctionDef) -> bool | None:  # noqa: N802
        if in_test(self.path, node) and (matched := m.extract(node, ASSERTS_IN_LOOP)) is not None:
            loop = matched["loop"]
            self.context.paths.add(self.path)
            self.context.diagnostics.append(
                Diagnostic(
                    relative_path(self.path, self.context.root),
                    self.get_metadata(cst.metadata.PositionProvider, loop),
                    normalise(loop),
                )
            )
        return super().visit_FunctionDef(node)


@register_rule_transformer(NoAssertsInLoop)
@attrs.define
class NoAssertsInLoopTransformer(BaseCstTransformer):
    pass
