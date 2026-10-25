def single_assertion() -> None:
    assert 2 > 1


def single_assertion_with_variables() -> None:
    a = 2
    b = 1
    assert a > b


def single_assertion_with_message() -> None:
    assert "abc" == "abc".lower(), "string should be lowered"
