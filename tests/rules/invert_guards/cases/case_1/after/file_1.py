def inverts_if_else_raise(a: int, b: int) -> float:
    if not b != 0:
        raise ValueError("b must not be 0")
    modified_a = a + 1
    return modified_a / b


def inverts_if_else_raise_with_multiple_failure_stmts(a: int, b: int) -> float:
    if not b != 0:
        print("invalid b value")
        raise ValueError("b must not be 0")
    modified_a = a + 1
    return modified_a / b


def leaves_func_unchanged(a: int, b: int) -> float:
    if b == 0:
        b += 1
    else:
        a += 1
    return a / b


def inverts_if_else_returns(a: int, b: int) -> float:
    if not b != 0:
        return b
    modified_a = a + 1
    return modified_a / b


def inverts_if_else_returns_with_multiple_failure_stmts(a: int, b: int) -> float:
    if not b != 0:
        print("invalid b value")
        return b
    modified_a = a + 1
    return modified_a / b
