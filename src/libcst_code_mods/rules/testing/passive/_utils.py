import libcst as cst


def in_test(path: str, node: cst.FunctionDef) -> bool:
    return path.rsplit("/", maxsplit=1)[-1].startswith("test_") and node.name.value.startswith("test_")
