import attrs
import libcst as cst
import libcst.matchers as m

from libcst_code_mods.core.base_cst_transformer import BaseCstTransformer
from libcst_code_mods.core.base_cst_visitor import BaseCstVisitor
from libcst_code_mods.core.refactoring_rule import RefactoringRule
from libcst_code_mods.rules._rule_mapping import register_rule, register_rule_transformer, register_rule_visitor


@register_rule
@attrs.define(frozen=True)
class InlineShortSingleUseVariables(RefactoringRule):
    """Examples:

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def single_use_variable_is_inlined() -> None:
                a = "something"
                b = fn(a=a)

        Post-transformer:

        .. code-block:: python

            def single_use_variable_is_inlined() -> None:
                b = fn(a="something")

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def variable_used_in_fstring_is_inlined_if_it_includes_quote_chars_they_are_changed_to_avoid_syntax_errors() -> None:
                isinstance_checks_str = ", ".join(isinstance_checks)
                message = f"{isinstance_checks_str}"

        Post-transformer:

        .. code-block:: python

            def variable_used_in_fstring_is_inlined_if_it_includes_quote_chars_they_are_changed_to_avoid_syntax_errors() -> None:
                message = f"{', '.join(isinstance_checks)}"

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def variable_used_in_subscript_is_inlined() -> None:
                block_body = list(updated_node.body.body)
                last = block_body[-1]

        Post-transformer:

        .. code-block:: python

            def variable_used_in_subscript_is_inlined() -> None:
                last = list(updated_node.body.body)[-1]

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def variable_used_as_method_receiver_is_inlined() -> None:
                cond = extracted["if_cond"]
                new_cond = cond.visit(transformer)

        Post-transformer:

        .. code-block:: python

            def variable_used_as_method_receiver_is_inlined() -> None:
                new_cond = extracted["if_cond"].visit(transformer)

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def variable_used_as_attribute_is_inlined() -> None:
                original_assign = original_node.body[0]
                value = original_assign.value

        Post-transformer:

        .. code-block:: python

            def variable_used_as_attribute_is_inlined() -> None:
                value = original_node.body[0].value

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def variable_used_in_attribute_update_is_inlined() -> None:
                updated_assign = updated_node.body[0]
                result = updated_assign.with_changes(value=result)

        Post-transformer:

        .. code-block:: python

            def variable_used_in_attribute_update_is_inlined() -> None:
                result = updated_node.body[0].with_changes(value=result)

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def single_use_list_comp_is_inlined() -> None:
                a = [f(x) for x in y]
                b = fn(a=a)

        Post-transformer:

        .. code-block:: python

            def single_use_list_comp_is_inlined() -> None:
                b = fn(a=[f(x) for x in y])
    ---
    """

    max_value_length: int = 30


ASSIGNMENT_MATCHER = m.SimpleStatementLine(
    body=[
        m.Assign(
            targets=[m.AssignTarget(target=m.SaveMatchedNode(m.Name(), "name"))],
            value=m.SaveMatchedNode(m.DoNotCare(), "value"),
        )
    ]
)


@register_rule_visitor(InlineShortSingleUseVariables)
@attrs.define
class InlineShortSingleUseVariablesVisitor(BaseCstVisitor):
    def visit_FunctionDef(self, node: cst.FunctionDef) -> bool | None:  # noqa: N802
        if m.findall(node.body, ASSIGNMENT_MATCHER):
            self.context.paths.add(self.path)
        return super().visit_FunctionDef(node)


@register_rule_transformer(InlineShortSingleUseVariables)
@attrs.define
class InlineShortSingleUseVariablesTransformer(BaseCstTransformer):
    max_value_length: int

    def leave_FunctionDef(  # noqa: N802
        self, original_node: cst.FunctionDef, updated_node: cst.FunctionDef
    ) -> cst.FunctionDef:
        if not (
            assignments := [
                (index, statement)
                for index, statement in enumerate(original_node.body.body)
                if m.matches(statement, ASSIGNMENT_MATCHER)
            ]
        ):
            return updated_node

        inlineable = []
        for assignment_index, assignment in assignments:
            extracted = m.extract(assignment, ASSIGNMENT_MATCHER)
            name = extracted["name"]
            value = extracted["value"]
            if len(cst.Module([]).code_for_node(value)) > self.max_value_length:
                continue

            names = m.findall(original_node.body, m.Name(value=name.value))
            assignment_targets = {
                target.target
                for target in m.findall(original_node.body, m.AssignTarget(target=m.Name(value=name.value)))
            }
            keyword_names = {
                argument.keyword for argument in m.findall(original_node.body, m.Arg(keyword=m.Name(value=name.value)))
            }
            attribute_names = {
                attribute.attr
                for attribute in m.findall(original_node.body, m.Attribute(attr=m.Name(value=name.value)))
            }
            uses = [
                node
                for node in names
                if node not in assignment_targets and node not in keyword_names and node not in attribute_names
            ]
            if len(uses) != 1:
                continue

            inlineable.append((assignment_index, name.value, value))

        body = list(updated_node.body.body)
        for assignment_index, name, value in reversed(inlineable):
            body = [
                statement.visit(_ReplaceName(name=name, replacement=value))
                for index, statement in enumerate(body)
                if index != assignment_index
            ]
        return updated_node.with_changes(body=updated_node.body.with_changes(body=body))


@attrs.define
class _ReplaceName(cst.CSTTransformer):
    name: str
    replacement: cst.BaseExpression

    def leave_Name(self, original_node: cst.Name, updated_node: cst.Name) -> cst.BaseExpression:  # noqa: N802
        if m.matches(original_node, m.Name(self.name)):
            if m.matches(self.replacement, m.SimpleString()):
                return self.replacement.with_changes(value=self.replacement.value.replace('"', "'"))
            return self.replacement
        return updated_node

    def leave_Arg(self, original_node: cst.Arg, updated_node: cst.Arg) -> cst.Arg:  # noqa: N802
        if original_node.keyword is not None and m.matches(original_node.keyword, m.Name(self.name)):
            return updated_node.with_changes(keyword=original_node.keyword)
        return updated_node

    def leave_FormattedStringExpression(  # noqa: N802
        self, original_node: cst.FormattedStringExpression, updated_node: cst.FormattedStringExpression
    ) -> cst.FormattedStringExpression:
        if m.matches(original_node, m.FormattedStringExpression(expression=m.Name(value=self.name))):
            replacement = self.replacement.visit(_UseSingleQuotes())
            return updated_node.with_changes(expression=replacement)
        return updated_node


class _UseSingleQuotes(cst.CSTTransformer):
    def leave_SimpleString(  # noqa: N802
        self, _original_node: cst.SimpleString, updated_node: cst.SimpleString
    ) -> cst.SimpleString:
        return updated_node.with_changes(value=updated_node.value.replace('"', "'"))
