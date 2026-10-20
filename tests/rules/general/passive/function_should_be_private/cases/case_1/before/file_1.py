def private_function_only_used_within_module(first: int, second: int) -> int:
    return first + second


result = private_function_only_used_within_module(3, 4)


def unused_public_function_stays_unchanged(value: int) -> int:
    return value


def _already_private_function_stays_unchanged(value: int) -> int:
    return value


private_result = _already_private_function_stays_unchanged(1)


def public_function_used_by_another_module_stays_public(value: int) -> int:
    return private_function_only_used_within_module(1, 2)


public_result = public_function_used_by_another_module_stays_public(1)
