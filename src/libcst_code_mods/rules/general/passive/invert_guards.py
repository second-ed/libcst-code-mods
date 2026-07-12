import attrs
import libcst as cst
import libcst.matchers as m

from libcst_code_mods.core.base_cst_transformer import BaseCstTransformer
from libcst_code_mods.core.base_cst_visitor import BaseCstVisitor
from libcst_code_mods.core.refactoring_rule import RefactoringRule
from libcst_code_mods.rules._cst_utils import invert_condition
from libcst_code_mods.rules._rule_mapping import register_rule, register_rule_transformer, register_rule_visitor


@register_rule
@attrs.define(frozen=True)
class InvertGuards(RefactoringRule):
    """Examples:

        Case:

        Pre-transformer:

        .. code-block:: python

            def inverts_if_else_raise(a: int, b: int) -> float:
                if b != 0:
                    modified_a = a + 1
                else:
                    raise ValueError("b must not be 0")
                return modified_a / b

        Post-transformer:

        .. code-block:: python

            def inverts_if_else_raise(a: int, b: int) -> float:
                if b == 0:
                    raise ValueError("b must not be 0")
                modified_a = a + 1
                return modified_a / b


        Case:

        Pre-transformer:

        .. code-block:: python

            def inverts_if_else_raise_with_multiple_failure_stmts(a: int, b: int) -> float:
                if b != 0:
                    modified_a = a + 1
                else:
                    print("invalid b value")
                    raise ValueError("b must not be 0")
                return modified_a / b

        Post-transformer:

        .. code-block:: python

            def inverts_if_else_raise_with_multiple_failure_stmts(a: int, b: int) -> float:
                if b == 0:
                    print("invalid b value")
                    raise ValueError("b must not be 0")
                modified_a = a + 1
                return modified_a / b


        Case:

        Pre-transformer:

        .. code-block:: python

            def inverts_if_else_returns(a: int, b: int) -> float:
                if b != 0:
                    modified_a = a + 1
                else:
                    return b
                return modified_a / b

        Post-transformer:

        .. code-block:: python

            def inverts_if_else_returns(a: int, b: int) -> float:
                if b == 0:
                    return b
                modified_a = a + 1
                return modified_a / b


        Case:

        Pre-transformer:

        .. code-block:: python

            def inverts_if_else_returns_with_multiple_failure_stmts(a: int, b: int) -> float:
                if b != 0:
                    modified_a = a + 1
                else:
                    print("invalid b value")
                    return b
                return modified_a / b

        Post-transformer:

        .. code-block:: python

            def inverts_if_else_returns_with_multiple_failure_stmts(a: int, b: int) -> float:
                if b == 0:
                    print("invalid b value")
                    return b
                modified_a = a + 1
                return modified_a / b


        Case:

        Pre-transformer:

        .. code-block:: python

            def invert_not_correctly() -> int | None:
                if not 1:
                    print("blah")
                else:
                    return 1

        Post-transformer:

        .. code-block:: python

            def invert_not_correctly() -> int | None:
                if 1:
                    return 1
                print("blah")


        Case:

        Pre-transformer:

        .. code-block:: python

            def nested_if(x: bool, y: bool) -> None:
                if x:
                    if y:
                        print("ok")
                    else:
                        raise ValueError()

        Post-transformer:

        .. code-block:: python

            def nested_if(x: bool, y: bool) -> None:
                if x:
                    if not y:
                        raise ValueError()
                    print("ok")


        Case:

        Pre-transformer:

        .. code-block:: python

            def double_raise_case(a: bool, b: bool) -> None:
                if a:
                    if b:
                        print("b")
                    else:
                        raise ValueError()
                else:
                    raise RuntimeError()

        Post-transformer:

        .. code-block:: python

            def double_raise_case(a: bool, b: bool) -> None:
                if not a:
                    raise RuntimeError()
                if not b:
                    raise ValueError()
                print("b")


        Case:

        Pre-transformer:

        .. code-block:: python

            def sibling_nested(a: bool, b: bool) -> None:
                if a:
                    print("before")

                    if b:
                        print("ok")
                    else:
                        raise ValueError()

                    print("after")

        Post-transformer:

        .. code-block:: python

            def sibling_nested(a: bool, b: bool) -> None:
                if a:
                    print("before")
                    if not b:
                        raise ValueError()
                    print("ok")

                    print("after")


        Case:

        Pre-transformer:

        .. code-block:: python

            def double_nested(a: bool, b: bool, c: bool) -> None:
                if a:
                    if b:
                        if c:
                            print("ok")
                        else:
                            raise ValueError()

        Post-transformer:

        .. code-block:: python

            def double_nested(a: bool, b: bool, c: bool) -> None:
                if a:
                    if b:
                        if not c:
                            raise ValueError()
                        print("ok")
    ::
    """


GUARD_MATCHER = m.If(
    test=m.SaveMatchedNode(m.DoNotCare(), "condition"),
    body=m.SaveMatchedNode(m.IndentedBlock(), "success_body"),
    orelse=m.Else(
        body=m.SaveMatchedNode(
            m.IndentedBlock(body=[m.ZeroOrMore(), m.SimpleStatementLine(body=[m.OneOf(m.Return(), m.Raise())])]),
            "failure_body",
        )
    ),
)


@register_rule_visitor(InvertGuards)
@attrs.define
class InvertGuardsVisitor(BaseCstVisitor):
    def visit_If(self, node: cst.If) -> bool | None:  # noqa: N802
        if m.matches(node, GUARD_MATCHER):
            self.context.paths.add(self.path)
        return super().visit_If(node)


@register_rule_transformer(InvertGuards)
@attrs.define
class InvertGuardsTransformer(BaseCstTransformer):
    def leave_If(self, original_node: cst.If, updated_node: cst.If) -> cst.If | cst.FlattenSentinel:  # noqa: N802
        parent = self.get_metadata(cst.metadata.ParentNodeProvider, original_node)

        if isinstance(parent, cst.If) and parent.orelse is original_node:
            return updated_node

        extracted = m.extract(updated_node, GUARD_MATCHER)

        if not extracted:
            return updated_node

        condition = extracted["condition"]
        success_body = list(extracted["success_body"].body)
        failure_body = list(extracted["failure_body"].body)

        if not failure_body:
            return updated_node

        last = failure_body[-1]

        if not isinstance(last, cst.SimpleStatementLine) or not isinstance(last.body[0], (cst.Return, cst.Raise)):
            return updated_node

        guard = cst.If(test=invert_condition(condition), body=cst.IndentedBlock(body=failure_body))
        return cst.FlattenSentinel([guard, *success_body])
