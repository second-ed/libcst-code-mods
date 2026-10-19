import libcst as cst


def in_test(path: str, node: cst.FunctionDef) -> bool:
    return in_test_file(path) and node.name.value.startswith("test_")


def in_test_file(path: str) -> bool:
    return path.rsplit("/", maxsplit=1)[-1].startswith("test_")
