def inverts_if_else_raise(a: int, b: int) -> float:
    if b != 0:
        modified_a = a + 1
    else:
        raise ValueError("b must not be 0")
    return modified_a / b


def leaves_func_unchanged(a: int, b: int) -> float:
    if b == 0:
        b += 1
    else:
        a += 1
    return a / b


def simple_loop_with_if_else() -> None:
    for i in range(10):
        if i % 2 == 0:
            print(f"{i} is even")
        else:
            print(f"{i} is odd")
