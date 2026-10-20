def _private_function(value: int) -> int:
    return value


def public_function() -> int:
    return _private_function(1)
