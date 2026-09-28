def a_fn_that_only_depends_on_its_args(a: int, b: int) -> int:
    res = a + b
    return res


def a_fn_that_depends_on_a_non_local_variable(a: int, b: int) -> int:
    res = a + b + C
    return res


def an_impure_fn_with_an_existing_docstring(a: int, b: int) -> int:
    """This function has an existing docstring

    Args:
        a (int): the first parameter
        b (int): the second parameter

    Returns:
        int: the sum of the 2 args
    """
    registry[a] = b
    registry[b] = C
    return a + b


def docstring_appending_is_idempontent(a: int, b: int) -> int:
    # [[Likely pure]]
    res = a + b
    return res


def parse(value: str) -> int:
    return int(value)


def size(value: str) -> int:
    return len(value)


def load(path: str) -> str:
    with open(path) as file:
        return file.read()


def combined(value: str) -> int:
    return size(parse(value))


def main(path: str) -> None:
    data = load(path)
    combined(data)
