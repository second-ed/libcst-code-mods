def single_assertion() -> None:
    if 2 <= 1:
        raise AssertionError("2 <= 1")


def single_assertion_with_variables() -> None:
    a = 2
    b = 1
    if a <= b:
        raise AssertionError("a <= b")


def single_assertion_with_message() -> None:
    if "abc" != "abc".lower():
        raise AssertionError("string should be lowered")
