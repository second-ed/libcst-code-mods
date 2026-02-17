def function_nested_function(a: int) -> int:
    def double(x: int) -> int:
        return x * 2

    return a + double(a - 1)
