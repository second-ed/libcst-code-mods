import libcst as cst


def normalise(node: cst.CSTNode) -> str:
    return cst.Module([]).code_for_node(node)
