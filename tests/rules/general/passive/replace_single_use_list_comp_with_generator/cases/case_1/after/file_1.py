def update_single_use_list_comp_to_gen_exp() -> None:
    values = (i + 1 for i in range(10))
    sum(values)


def does_not_update_dict_or_set_comp() -> None:
    values = {i + 1 for i in range(10)}
    mapping = {k: k * 2 for k in range(5)}
    sum(values)
    sum(mapping.values())


def does_not_update_if_the_list_comp_is_used_twice() -> None:
    values = [i + 1 for i in range(10)]
    _total = sum(values) + sum(values)
