import attrs
import libcst as cst
import libcst.matchers as m

from libcst_code_mods.core.base_cst_transformer import BaseCstTransformer
from libcst_code_mods.core.base_cst_visitor import BaseCstVisitor
from libcst_code_mods.core.refactoring_rule import RefactoringRule
from libcst_code_mods.rules._cst_utils import normalise
from libcst_code_mods.rules._rule_mapping import register_rule_transformer, register_rule_visitor


@attrs.define(frozen=True)
class ReplaceMutableDefaultsWithGuardClause(RefactoringRule):
    pass


@register_rule_visitor(ReplaceMutableDefaultsWithGuardClause)
@attrs.define
class ReplaceMutableDefaultsWithGuardClauseVisitor(BaseCstVisitor):
    mutable_params: dict[str, dict[str, str]] = attrs.field(factory=dict)

    def visit_FunctionDef(self, node: cst.FunctionDef) -> None:  # noqa: N802
        qualified_names = self.get_metadata(cst.metadata.FullyQualifiedNameProvider, node, set())

        if not qualified_names:
            return

        fqn = next(iter(qualified_names))

        if not isinstance(fqn, cst.metadata.QualifiedName):
            return

        for param in node.params.params:
            if param.default is not None and m.matches(
                param.default, m.OneOf(m.List(), m.Dict(), m.Set(), m.Call(m.Name("list")), m.Call(m.Name("set")))
            ):
                self.mutable_params.setdefault(fqn.name, {})
                self.mutable_params[fqn.name][param.name.value] = normalise(param.default)

        if self.mutable_params:
            self.context.paths.add(self.path)
            self.context.data.setdefault("mutable_params", {}).update(self.mutable_params)


@register_rule_transformer(ReplaceMutableDefaultsWithGuardClause)
@attrs.define
class ReplaceMutableDefaultsWithGuardClauseTransformer(BaseCstTransformer):
    mutable_params: dict[str, dict[str, str]]

    def leave_FunctionDef(self, original_node: cst.FunctionDef, updated_node: cst.FunctionDef) -> cst.FunctionDef:  # noqa: N802
        qualified_names = self.get_metadata(cst.metadata.FullyQualifiedNameProvider, original_node, set())

        if not qualified_names:
            return updated_node

        fqn = next(iter(qualified_names))

        if not isinstance(fqn, cst.metadata.QualifiedName) or fqn.name not in self.mutable_params:
            return updated_node

        params = self._update_params(updated_node, self.mutable_params[fqn.name])
        guards = [
            cst.parse_statement(f"{name} = {name} if {name} is not None else {default}")
            for name, default in self.mutable_params[fqn.name].items()
        ]
        new_body = [*guards, *updated_node.body.body]
        return updated_node.with_changes(
            params=updated_node.params.with_changes(params=params), body=updated_node.body.with_changes(body=new_body)
        )

    def _update_params(self, updated_node: cst.FunctionDef, fn_param_map: dict[str, str]) -> list[cst.Param]:
        new_params = []

        for param in updated_node.params.params:
            mutable = fn_param_map.get(param.name.value)

            if mutable is None:
                new_params.append(param)
                continue

            annotation = param.annotation

            if annotation is not None:
                annotation = cst.Annotation(
                    cst.BinaryOperation(left=annotation.annotation, operator=cst.BitOr(), right=cst.Name("None"))
                )

            new_params.append(param.with_changes(default=cst.Name("None"), annotation=annotation))
        return new_params
