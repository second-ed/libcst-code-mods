def function_nested_raises(a: int, b: int) -> int:
    if a > b:
        raise ValueError("a can not be greater than b")
    return a + b
