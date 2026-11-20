def identity_and() -> None:
    _ = A and True


def identity_or() -> None:
    _ = A or False


def domination_and() -> None:
    _ = A and False


def domination_or() -> None:
    _ = A or True


def idempotent_and() -> None:
    _ = A and A


def idempotent_or() -> None:
    _ = A or A


def complement_and() -> None:
    _ = A and not A


def complement_or() -> None:
    _ = A or not A


def absorption_or() -> None:
    _ = A or (A and B)


def absorption_and() -> None:
    _ = A and (A or B)


def double_negation() -> None:
    _ = not not A


def demorgan_and() -> None:
    _ = not (A and B)


def demorgan_or() -> None:
    _ = not (A or B)


def constant_not_true() -> None:
    _ = not True


def constant_not_false() -> None:
    _ = not False


def composite_identity_and_and_absorption_or() -> None:
    _ = (A and True) and (A or (A and B))


def composite_factor_and_or() -> None:
    _ = (A and B) or (A and not B)


def composite_factor_or_and() -> None:
    _ = (A or B) and (A or not B)


def composite_factor_and_or_common_right() -> None:
    _ = (A and B) or (not A and B)


def composite_factor_or_and_common_right() -> None:
    _ = (A or B) and (not A or B)


def flattened_composite_factor() -> None:
    _ = (A and B and C) or (A and not B and C)


# more complex ones
def composite_a() -> None:
    _ = (A or B) and (A or C)


def composite_b() -> None:
    _ = A and B and (not B and C or A and C)


def composite_c() -> None:
    _ = (A or not B or not C) and (A or not B or C) and (A or B or not C)
