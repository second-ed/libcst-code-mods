import libcst as cst


def normalise(node: cst.CSTNode | None) -> str:
    return cst.Module([]).code_for_node(node)
