def a_fn_that_only_depends_on_its_args(a: int, b: int) -> int:
    # [[Likely pure]]
    res = a + b
    return res


def a_fn_that_depends_on_a_non_local_variable(a: int, b: int) -> int:
    # [[Impure]]: Depends on [`C`] which do not originate within this function.
    res = a + b + C
    return res


def an_impure_fn_with_an_existing_docstring(a: int, b: int) -> int:
    # [[Impure]]: Depends on [`registry`, `C`] which do not originate within this function.
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
