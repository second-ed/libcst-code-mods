# repo-map-desc: simple filters that are applied before the transformation

import libcst as cst


def is_global_scope(scope: cst.metadata.Scope) -> bool:
    return isinstance(scope, cst.metadata.scope_provider.GlobalScope)


def is_class_scope(scope: cst.metadata.Scope) -> bool:
    return isinstance(scope, cst.metadata.scope_provider.ClassScope)


def is_function_scope(scope: cst.metadata.Scope) -> bool:
    return isinstance(scope, cst.metadata.scope_provider.FunctionScope)


def is_nested_function(qualified_names: set[cst.metadata.QualifiedName]) -> bool:
    return any("<locals>" in qn.name for qn in qualified_names)
