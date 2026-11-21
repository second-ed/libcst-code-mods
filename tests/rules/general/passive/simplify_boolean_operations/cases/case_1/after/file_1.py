def identity_and() -> None:
    _ = A


def identity_or() -> None:
    _ = A


def domination_and() -> None:
    _ = False


def domination_or() -> None:
    _ = True


def idempotent_and() -> None:
    _ = A


def idempotent_or() -> None:
    _ = A


def complement_and() -> None:
    _ = False


def complement_or() -> None:
    _ = True


def absorption_or() -> None:
    _ = A


def absorption_and() -> None:
    _ = A


def double_negation() -> None:
    _ = A


def demorgan_and() -> None:
    _ = not A or not B


def demorgan_or() -> None:
    _ = not A and not B


def constant_not_true() -> None:
    _ = False


def constant_not_false() -> None:
    _ = True


def composite_identity_and_and_absorption_or() -> None:
    _ = A


def composite_factor_and_or() -> None:
    _ = A


def composite_factor_or_and() -> None:
    _ = A


def composite_factor_and_or_common_right() -> None:
    _ = B


def composite_factor_or_and_common_right() -> None:
    _ = B


def flattened_composite_factor() -> None:
    _ = A and C


# more complex ones
def composite_a() -> None:
    _ = A or (B and C)


def composite_b() -> None:
    _ = A and B and C


def composite_c() -> None:
    _ = A or not B and not C


def more_absorption_law() -> None:
    _ = A


def demorgan_double_negation() -> None:
    _ = True


def all_possible_branches() -> None:
    _ = True


def conjunction_of_zero() -> None:
    _ = False


def absorption_across_multiple_terms() -> None:
    _ = A and (B or C) or (B and C)


def simplify_four_terms() -> None:
    _ = C or not A
