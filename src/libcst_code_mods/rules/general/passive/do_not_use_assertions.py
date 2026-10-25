import attrs
import libcst as cst
import libcst.matchers as m

from libcst_code_mods.core.base_cst_transformer import BaseCstTransformer
from libcst_code_mods.core.base_cst_visitor import BaseCstVisitor
from libcst_code_mods.core.refactoring_rule import RefactoringRule
from libcst_code_mods.cst_builders.primitives.declarations import cst_stmt
from libcst_code_mods.cst_builders.primitives.expressions import cst_call
from libcst_code_mods.cst_builders.primitives.literals import cst_str
from libcst_code_mods.rules._cst_utils import invert_condition, normalise
from libcst_code_mods.rules._rule_mapping import register_rule, register_rule_transformer, register_rule_visitor
from libcst_code_mods.rules.testing.passive._utils import in_test_file

ASSERTION_LINE = m.SimpleStatementLine(body=[m.SaveMatchedNode(m.Assert(), "assertion")])


@register_rule
@attrs.define(frozen=True)
class DoNotUseAssertions(RefactoringRule):
    """Examples:

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def single_assertion() -> None:
                assert 2 > 1

        Post-transformer:

        .. code-block:: python

            def single_assertion() -> None:
                if 2 <= 1:
                    raise AssertionError("2 <= 1")

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def single_assertion_with_variables() -> None:
                a = 2
                b = 1
                assert a > b

        Post-transformer:

        .. code-block:: python

            def single_assertion_with_variables() -> None:
                a = 2
                b = 1
                if a <= b:
                    raise AssertionError("a <= b")

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def single_assertion_with_message() -> None:
                assert "abc" == "abc".lower(), "string should be lowered"

        Post-transformer:

        .. code-block:: python

            def single_assertion_with_message() -> None:
                if "abc" != "abc".lower():
                    raise AssertionError("string should be lowered")
    ---
    """


@register_rule_visitor(DoNotUseAssertions)
@attrs.define
class DoNotUseAssertionsVisitor(BaseCstVisitor):
    def visit_Assert(self, node: cst.Assert) -> bool | None:  # noqa: N802
        if not in_test_file(self.path):
            self.context.paths.add(self.path)
        return super().visit_Assert(node)


@register_rule_transformer(DoNotUseAssertions)
@attrs.define
class DoNotUseAssertionsTransformer(BaseCstTransformer):
    def leave_SimpleStatementLine(  # noqa: N802
        self, _original_node: cst.SimpleStatementLine, updated_node: cst.SimpleStatementLine
    ) -> cst.BaseStatement:
        if (matched := m.extract(updated_node, ASSERTION_LINE)) is None:
            return updated_node

        assertion: cst.Assert = matched["assertion"]
        condition = invert_condition(assertion.test)
        message = assertion.msg or cst_str(normalise(condition))
        raise_statement = cst_stmt(cst.Raise(exc=cst_call("AssertionError", [message])))
        return cst.If(
            test=condition, body=cst.IndentedBlock(body=[raise_statement]), leading_lines=updated_node.leading_lines
        )
