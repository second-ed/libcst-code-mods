import attrs
import libcst as cst
import libcst.matchers as m

from libcst_code_mods.core.base_cst_transformer import BaseCstTransformer
from libcst_code_mods.core.base_cst_visitor import BaseCstVisitor
from libcst_code_mods.core.refactoring_rule import RefactoringRule
from libcst_code_mods.rules._rule_mapping import register_rule, register_rule_transformer, register_rule_visitor
from libcst_code_mods.rules.general.passive._dataclass_decorator_utils import make_decorator_arg_true


@register_rule
@attrs.define(frozen=True)
class DataclassesShouldHaveSlots(RefactoringRule):
    """Examples:

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            @dataclass(frozen=True)
            class SomeDataclass:
                pass

        Post-transformer:

        .. code-block:: python

            @dataclass(frozen=True, slots=True)
            class SomeDataclass:
                pass
    ---
    """


@register_rule_visitor(DataclassesShouldHaveSlots)
@attrs.define
class DataclassesShouldHaveSlotsVisitor(BaseCstVisitor):
    def visit_ClassDef(self, node: cst.ClassDef) -> None:  # noqa: N802
        if any(m.matches(decorator, SLOTS_DECORATOR) for decorator in node.decorators):
            self.context.paths.add(self.path)


@register_rule_transformer(DataclassesShouldHaveSlots)
@attrs.define
class DataclassesShouldHaveSlotsTransformer(BaseCstTransformer):
    def leave_ClassDef(  # noqa: N802
        self,
        original_node: cst.ClassDef,  # noqa: ARG002
        updated_node: cst.ClassDef,
    ) -> cst.ClassDef:
        decorators = [
            make_decorator_arg_true(decorator, "slots") if m.matches(decorator, SLOTS_DECORATOR) else decorator
            for decorator in updated_node.decorators
        ]
        return updated_node.with_changes(decorators=decorators)


SLOTS_DECORATOR = m.Decorator(decorator=m.OneOf(m.Name("dataclass"), m.Call(m.Name("dataclass"))))
