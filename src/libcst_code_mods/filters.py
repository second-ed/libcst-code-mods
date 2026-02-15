import libcst as cst

from libcst_code_mods.node_collector import NodeMetadata


def is_global_scope(node_metadata: NodeMetadata) -> bool:
    return isinstance(node_metadata.scope, cst.metadata.scope_provider.GlobalScope)


def is_class_scope(node_metadata: NodeMetadata) -> bool:
    return isinstance(node_metadata.scope, cst.metadata.scope_provider.ClassScope)


def is_function_scope(node_metadata: NodeMetadata) -> bool:
    return isinstance(node_metadata.scope, cst.metadata.scope_provider.FunctionScope)


def is_nested_function(node_metadata: NodeMetadata) -> bool:
    return any("<locals>" in qn.name for qn in node_metadata.qualified_names)
