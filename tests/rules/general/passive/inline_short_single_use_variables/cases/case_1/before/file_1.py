def single_use_variable_is_inlined() -> None:
    a = "something"
    b = fn(a=a)


def multi_use_variable_is_unchanged() -> None:
    a = "something"
    b = super_long_function_name_that_is_longer_than_the_limit(a=a)
    c = fn2(b, a=a)


def variable_is_unchanged_if_variable_value_is_too_long() -> None:
    z = [some_long_function_name(x) for x in y if a]
    b = fn(z=z)


def single_use_list_comp_is_inlined() -> None:
    a = [f(x) for x in y]
    b = fn(a=a)
