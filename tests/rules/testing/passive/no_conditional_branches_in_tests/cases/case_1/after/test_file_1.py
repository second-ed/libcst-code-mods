def test_without_if_elses_should_not_raise() -> None:
    assert len([0, 1, 2]) == 3


def test_with_if_and_elses_should_trigger_diagnostic() -> None:
    if a:
        res = 1 == 1
    else:
        res = 1 == 0
    assert res


def test_if_without_else_should_not_trigger() -> None:
    if a:
        result = 1


def test_if_else_chain_should_trigger() -> None:
    if a:
        result = 1
    elif b:
        result = 2
    else:
        result = 3


def test_comprehension_should_not_trigger() -> None:
    result = [value if condition else fallback for value in values]
    filtered = [value for value in values if condition]
