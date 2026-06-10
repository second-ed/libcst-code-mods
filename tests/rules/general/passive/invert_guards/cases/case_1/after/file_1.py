def inverts_if_else_raise(a: int, b: int) -> float:
    if b == 0:
        raise ValueError("b must not be 0")
    modified_a = a + 1
    return modified_a / b


def inverts_if_else_raise_with_multiple_failure_stmts(a: int, b: int) -> float:
    if b == 0:
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
    if b == 0:
        return b
    modified_a = a + 1
    return modified_a / b


def inverts_if_else_returns_with_multiple_failure_stmts(a: int, b: int) -> float:
    if b == 0:
        print("invalid b value")
        return b
    modified_a = a + 1
    return modified_a / b


def leaves_elif_func_unchanged(a: int, b: int) -> float:
    if b == 0:
        b += 1
    elif a == 0:
        a += 2
    else:
        a += 1
    return a / b


def invert_not_correctly() -> int | None:
    if 1:
        return 1
    print("blah")


def nested_if(x: bool, y: bool) -> None:
    if x:
        if not y:
            raise ValueError()
        print("ok")


def double_raise_case(a: bool, b: bool) -> None:
    if not a:
        raise RuntimeError()
    if not b:
        raise ValueError()
    print("b")


def sibling_nested(a: bool, b: bool) -> None:
    if a:
        print("before")
        if not b:
            raise ValueError()
        print("ok")

        print("after")


def double_nested(a: bool, b: bool, c: bool) -> None:
    if a:
        if b:
            if not c:
                raise ValueError()
            print("ok")


def leaves_elif_return_func_unchanged(a: int, b: int) -> float:
    if b == 0:
        b += 1
    elif a == 0:
        a += 2
    else:
        return a / b
    return a * b
