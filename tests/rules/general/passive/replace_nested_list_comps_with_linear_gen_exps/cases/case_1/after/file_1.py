def nested_comps_with_depth_1(y: list) -> None:
    z = list(map(fn_1, y))


def nested_comps_with_depth_1_and_filters_1(y: list) -> None:
    __s = filter(fil_1, y)
    z = list(map(fn_1, __s))


def nested_comps_with_depth_2(y: list) -> None:
    __s = map(fn_1, y)
    z = list(map(fn_2, __s))


def nested_comps_with_depth_2_and_filters_1(y: list) -> None:
    __s = filter(fil_1, y)
    __s = map(fn_1, __s)
    z = list(map(fn_2, __s))


def nested_comps_with_depth_2_and_filters_2(y: list) -> None:
    __s = filter(fil_1, y)
    __s = map(fn_1, __s)
    __s = filter(fil_2, __s)
    z = list(map(fn_2, __s))


def nested_comps_with_depth_3(y: list) -> None:
    __s = map(fn_1, y)
    __s = map(fn_2, __s)
    z = list(map(fn_3, __s))


def nested_comps_with_depth_3_and_filters_1(y: list) -> None:
    __s = filter(fil_1, y)
    __s = map(fn_1, __s)
    __s = map(fn_2, __s)
    z = list(map(fn_3, __s))


def nested_comps_with_depth_3_and_filters_2(y: list) -> None:
    __s = filter(fil_1, y)
    __s = map(fn_1, __s)
    __s = filter(fil_2, __s)
    __s = map(fn_2, __s)
    z = list(map(fn_3, __s))


def nested_comps_with_depth_3_and_filters_3(y: list) -> None:
    __s = filter(fil_1, y)
    __s = map(fn_1, __s)
    __s = filter(fil_2, __s)
    __s = map(fn_2, __s)
    __s = filter(fil_3, __s)
    z = list(map(fn_3, __s))


def nested_comps_with_depth_4(y: list) -> None:
    __s = map(fn_1, y)
    __s = map(fn_2, __s)
    __s = map(fn_3, __s)
    z = list(map(fn_4, __s))


def nested_comps_with_depth_4_and_filters_1(y: list) -> None:
    __s = filter(fil_1, y)
    __s = map(fn_1, __s)
    __s = map(fn_2, __s)
    __s = map(fn_3, __s)
    z = list(map(fn_4, __s))


def nested_comps_with_depth_4_and_filters_2(y: list) -> None:
    __s = filter(fil_1, y)
    __s = map(fn_1, __s)
    __s = filter(fil_2, __s)
    __s = map(fn_2, __s)
    __s = map(fn_3, __s)
    z = list(map(fn_4, __s))


def nested_comps_with_depth_4_and_filters_3(y: list) -> None:
    __s = filter(fil_1, y)
    __s = map(fn_1, __s)
    __s = filter(fil_2, __s)
    __s = map(fn_2, __s)
    __s = filter(fil_3, __s)
    __s = map(fn_3, __s)
    z = list(map(fn_4, __s))


def nested_comps_with_depth_4_and_filters_4(y: list) -> None:
    __s = filter(fil_1, y)
    __s = map(fn_1, __s)
    __s = filter(fil_2, __s)
    __s = map(fn_2, __s)
    __s = filter(fil_3, __s)
    __s = map(fn_3, __s)
    __s = filter(fil_4, __s)
    z = list(map(fn_4, __s))
