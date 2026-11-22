import attrs
import libcst as cst
import libcst.matchers as m

from libcst_code_mods.core.base_cst_transformer import BaseCstTransformer
from libcst_code_mods.core.base_cst_visitor import BaseCstVisitor
from libcst_code_mods.core.refactoring_rule import RefactoringRule
from libcst_code_mods.rules._rule_mapping import register_rule, register_rule_transformer, register_rule_visitor


@register_rule
@attrs.frozen
class ReorderFunctions(RefactoringRule):
    reorder_paths: list[str]


@register_rule_visitor(ReorderFunctions)
@attrs.define
class ReorderFunctionsVisitor(BaseCstVisitor):
    reorder_paths: list[str]

    def leave_Module(self, original_node: cst.Module) -> None:  # noqa: N802
        if self.path in self.reorder_paths:
            self.context.paths.add(self.path)
        return super().leave_Module(original_node)


@register_rule_transformer(ReorderFunctions)
@attrs.define
class ReorderFunctionsTransformer(BaseCstTransformer):
    def leave_Module(self, original_node: cst.Module, updated_node: cst.Module) -> cst.Module:  # noqa: ARG002, N802

        import_nodes, assign_nodes, fn_nodes, class_nodes = [], [], {}, []

        for node in updated_node.body:
            if m.matches(node, m.SimpleStatementLine([m.OneOf(m.Import(), m.ImportFrom())])):
                import_nodes.append(node)
            elif m.matches(node, m.SimpleStatementLine([m.OneOf(m.AnnAssign(), m.Assign())])):
                assign_nodes.append(node)
            elif m.matches(node, m.ClassDef()):
                class_nodes.append(node)
            elif m.matches(node, m.FunctionDef()):
                fn_nodes[node.name.value] = node

        calls = _populate_call_visitors(fn_nodes)

        fn_nodes = [fn_nodes[fn.name] for fn in _sort_functions(calls)]
        return updated_node.with_changes(body=[*import_nodes, *class_nodes, *fn_nodes, *assign_nodes])


def _populate_call_visitors(fn_nodes: dict[str, cst.FunctionDef]) -> dict[str, list[str]]:
    calls = {}

    for name, fn in fn_nodes.items():
        visitor = CallCounter(name, list(fn_nodes))
        fn.visit(visitor)
        calls.setdefault(name, []).extend(visitor.calls)
    return calls


@attrs.define
class CallCounter(cst.CSTVisitor):
    fn_name: str
    module_names: list[str]
    calls: list[str] = attrs.field(factory=list)

    def visit_Call(self, node: cst.Call) -> bool | None:  # noqa: N802
        if node.func.value in self.module_names:
            self.calls.append(node.func.value)
        return super().visit_Call(node)


@attrs.frozen
class FnCallStats:
    name: str
    calls: list[str]
    called_by: list[str]


def _sort_functions(calls: dict[str, list[str]]) -> list[FnCallStats]:
    called_by = {name: [] for name in calls}
    for caller, callees in calls.items():
        for callee in dict.fromkeys(callees):
            called_by.setdefault(callee, []).append(caller)

    return sorted(
        (FnCallStats(name, list(dict.fromkeys(calls.get(name, []))), callers) for name, callers in called_by.items()),
        key=lambda f: (len(f.called_by), -len(f.calls), f.name.strip("_")),
    )
