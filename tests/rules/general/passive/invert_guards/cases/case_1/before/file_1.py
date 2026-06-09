def inverts_if_else_raise(a: int, b: int) -> float:
    if b != 0:
        modified_a = a + 1
    else:
        raise ValueError("b must not be 0")
    return modified_a / b


def inverts_if_else_raise_with_multiple_failure_stmts(a: int, b: int) -> float:
    if b != 0:
        modified_a = a + 1
    else:
        print("invalid b value")
        raise ValueError("b must not be 0")
    return modified_a / b


def leaves_func_unchanged(a: int, b: int) -> float:
    if b == 0:
        b += 1
    else:
        a += 1
    return a / b


def inverts_if_else_returns(a: int, b: int) -> float:
    if b != 0:
        modified_a = a + 1
    else:
        return b
    return modified_a / b


def inverts_if_else_returns_with_multiple_failure_stmts(a: int, b: int) -> float:
    if b != 0:
        modified_a = a + 1
    else:
        print("invalid b value")
        return b
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
    if not 1:
        print("blah")
    else:
        return 1


def nested_if(x: bool, y: bool) -> None:
    if x:
        if y:
            print("ok")
        else:
            raise ValueError()


def double_raise_case(a: bool, b: bool) -> None:
    if a:
        if b:
            print("b")
        else:
            raise ValueError()
    else:
        raise RuntimeError()


def sibling_nested(a: bool, b: bool) -> None:
    if a:
        print("before")

        if b:
            print("ok")
        else:
            raise ValueError()

        print("after")


def double_nested(a: bool, b: bool, c: bool) -> None:
    if a:
        if b:
            if c:
                print("ok")
            else:
                raise ValueError()
