import attrs
import libcst as cst
import libcst.matchers as m

from libcst_code_mods.core.base_cst_transformer import BaseCstTransformer
from libcst_code_mods.core.base_cst_visitor import BaseCstVisitor
from libcst_code_mods.core.refactoring_rule import RefactoringRule
from libcst_code_mods.rules._rule_mapping import register_rule, register_rule_transformer, register_rule_visitor


@register_rule
@attrs.define(frozen=True)
class DataclassesShouldBeFrozen(RefactoringRule):
    """Examples:

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            @dataclass(slots=True)
            class SomeDataclass:
                pass

        Post-transformer:

        .. code-block:: python

            @dataclass(slots=True, frozen=True)
            class SomeDataclass:
                pass

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            @attrs.define
            class SomeAttrsClass:
                pass

        Post-transformer:

        .. code-block:: python

            @attrs.define(frozen=True)
            class SomeAttrsClass:
                pass
    ---
    """


@register_rule_visitor(DataclassesShouldBeFrozen)
@attrs.define
class DataclassesShouldBeFrozenVisitor(BaseCstVisitor):
    def visit_ClassDef(self, node: cst.ClassDef) -> None:  # noqa: N802
        if any(m.matches(decorator, FROZEN_DECORATOR) for decorator in node.decorators):
            self.context.paths.add(self.path)


@register_rule_transformer(DataclassesShouldBeFrozen)
@attrs.define
class DataclassesShouldBeFrozenTransformer(BaseCstTransformer):
    def leave_ClassDef(  # noqa: N802
        self,
        original_node: cst.ClassDef,  # noqa: ARG002
        updated_node: cst.ClassDef,
    ) -> cst.ClassDef:
        decorators = [
            _make_frozen_decorator(decorator) if m.matches(decorator, FROZEN_DECORATOR) else decorator
            for decorator in updated_node.decorators
        ]
        return updated_node.with_changes(decorators=decorators)


FROZEN_DECORATOR = m.Decorator(
    decorator=m.OneOf(
        m.Name("dataclass"),
        m.Call(m.Name("dataclass")),
        m.Attribute(value=m.Name("attrs"), attr=m.Name("define")),
        m.Call(m.Attribute(value=m.Name("attrs"), attr=m.Name("define"))),
    )
)


def _make_frozen_decorator(decorator: cst.Decorator) -> cst.Decorator:
    if m.matches(decorator, m.Decorator(decorator=m.OneOf(m.Name(), m.Attribute()))):
        call = cst.Call(func=decorator.decorator, args=[cst.Arg(keyword=cst.Name("frozen"), value=cst.Name("True"))])
        return decorator.with_changes(decorator=call)

    matched = m.extract(decorator, m.Decorator(decorator=m.SaveMatchedNode(m.Call(), "call")))
    if matched is None:
        return decorator

    call = matched["call"]
    if any(m.matches(arg, m.Arg(keyword=m.Name("frozen"), value=m.DoNotCare())) for arg in call.args):
        args = [
            arg.with_changes(value=cst.Name("True"))
            if m.matches(arg, m.Arg(keyword=m.Name("frozen"), value=m.DoNotCare()))
            else arg
            for arg in call.args
        ]
    else:
        args = [*call.args, cst.Arg(keyword=cst.Name("frozen"), value=cst.Name("True"))]

    return decorator.with_changes(decorator=call.with_changes(args=args))
