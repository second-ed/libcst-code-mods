def process_a(obj, value) -> None:
    cleaned = obj.clean(value)
    save(cleaned, limit=10)


def transform_a(some_arg, guards):
    res_a, res_b = fn_a(some_arg)
    return some_arg.update(body=some_arg.body.update(body=[*res_a, guards, *some_arg.body.body[res_b:]]))


def transform_with_early_return(some_arg, guards):
    res_a, res_b = fn_a(some_arg)
    if not some_arg:
        return some_arg
    return some_arg.update(body=some_arg.body.update(body=[*res_a, guards, *some_arg.body.body[res_b:]]))
