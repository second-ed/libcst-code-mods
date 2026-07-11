def func(a: int, b: str, c: float) -> str:
    """some test multi line docstring

    Args:
        a (int): _description_
        b (str): _description_
        c (float): _description_

    Returns:
        str: _description_
    """
    if a % 2 == 0:
        return b + str(c)
    return str(c)
