def if_stmt_to_and() -> None:
    if 1 == 1 & 2 == 2:
        print("condition is true")


def if_stmt_to_or() -> None:
    if 1 == 1 | 2 == 2:
        print("condition is true")


def multiple_conds_with_ands_and_ors() -> None:
    if (1 == 1 & 2 == 2) & (1 == 1 | 2 == 2):
        print("condition is true")
    elif 1 == 1 & 2 == 2 | 3 == 3:
        print("condition is true")


def should_not_change_if_bitwise_is_not_top_level(df) -> None:
    if df[df["a"] & df["b"]].all():
        print("condition is true")
    elif df.filter(col("a") & col("b")).all():
        print("condition is true")
    elif df.filter(col("a") & col("b")).all() & 1 == 1:
        print("condition is true")


def should_not_change_this_fn() -> None:
    if 1 == 1 and 2 == 2:
        print("condition is true")
