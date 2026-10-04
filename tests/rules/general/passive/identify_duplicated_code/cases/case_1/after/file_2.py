def process_b(table, item) -> None:
    result = table.clean(item)
    save(result, limit=50)


def transform_b(some_arg, debugs):
    res_a, res_b = fn_a(some_arg)
    return some_arg.update(body=some_arg.body.update(body=[*res_a, debugs, *some_arg.body.body[res_b:]]))


def invalid_match_because_of_attr_name(some_arg, debugs):
    res_a, res_b = fn_a(some_arg)
    return some_arg.update(body=some_arg.body.update(body=[*res_a, debugs, *some_arg.different.body[res_b:]]))


def transform_with_early_return(some_arg, guards):
    res_a, res_b = fn_a(some_arg)
    if not some_arg:
        return some_arg
    return some_arg.update(body=some_arg.body.update(body=[*res_a, guards, *some_arg.body.body[res_b:]]))
