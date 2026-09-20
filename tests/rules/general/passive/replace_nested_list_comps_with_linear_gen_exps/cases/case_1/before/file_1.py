def nested_comps_with_depth_1(y: list) -> None:
    z = [fn_1(a) for a in y]


def nested_comps_with_depth_1_and_filters_1(y: list) -> None:
    z = [fn_1(a) for a in y if fil_1(a)]


def nested_comps_with_depth_2(y: list) -> None:
    z = (fn_2(b) for b in (fn_1(a) for a in y))


def nested_comps_with_depth_2_and_filters_1(y: list) -> None:
    z = [fn_2(b) for b in [fn_1(a) for a in y if fil_1(a)]]


def nested_comps_with_depth_2_and_filters_2(y: list) -> None:
    z = [fn_2(b) for b in [fn_1(a) for a in y if fil_1(a)] if fil_2(b)]


def nested_comps_with_depth_3(y: list) -> None:
    z = [fn_3(c) for c in [fn_2(b) for b in [fn_1(a) for a in y]]]


def nested_comps_with_depth_3_and_filters_1(y: list) -> None:
    z = [fn_3(c) for c in [fn_2(b) for b in [fn_1(a) for a in y if fil_1(a)]]]


def nested_comps_with_depth_3_and_filters_2(y: list) -> None:
    z = [fn_3(c) for c in [fn_2(b) for b in [fn_1(a) for a in y if fil_1(a)] if fil_2(b)]]


def nested_comps_with_depth_3_and_filters_3(y: list) -> None:
    z = [fn_3(c) for c in [fn_2(b) for b in [fn_1(a) for a in y if fil_1(a)] if fil_2(b)] if fil_3(c)]


def nested_comps_with_depth_4(y: list) -> None:
    z = [fn_4(d) for d in [fn_3(c) for c in [fn_2(b) for b in [fn_1(a) for a in y]]]]


def nested_comps_with_depth_4_and_filters_1(y: list) -> None:
    z = [fn_4(d) for d in [fn_3(c) for c in [fn_2(b) for b in [fn_1(a) for a in y if fil_1(a)]]]]


def nested_comps_with_depth_4_and_filters_2(y: list) -> None:
    z = [fn_4(d) for d in [fn_3(c) for c in [fn_2(b) for b in [fn_1(a) for a in y if fil_1(a)] if fil_2(b)]]]


def nested_comps_with_depth_4_and_filters_3(y: list) -> list:
    return [
        fn_4(d) for d in [fn_3(c) for c in [fn_2(b) for b in [fn_1(a) for a in y if fil_1(a)] if fil_2(b)] if fil_3(c)]
    ]


def nested_comps_with_depth_4_and_filters_4(y: list) -> None:
    z = [
        fn_4(d)
        for d in [fn_3(c) for c in [fn_2(b) for b in [fn_1(a) for a in y if fil_1(a)] if fil_2(b)] if fil_3(c)]
        if fil_4(d)
    ]


def nested_comps_with_multiple_fn_calls(y: list) -> None:
    z = [fn_2(fn_1(a)) for a in y if fil_2(fil_1(a))]


def should_not_change_uses_kwarg_in_fns(y: list, b: int) -> None:
    z = [fn_1(a, b=b) for a in y if fil_1(a, b=b)]


def unrelated_fn(a: int, b: int) -> int:
    return a + b
