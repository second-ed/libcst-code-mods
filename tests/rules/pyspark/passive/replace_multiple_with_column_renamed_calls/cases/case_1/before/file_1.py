def one_with_column_renamed_call_left_unchanged() -> None:
    df.withColumnRenamed("a", "x")


def two_with_column_renamed_calls_in_a_row() -> None:
    df.withColumnRenamed("a", "x").withColumnRenamed("b", "y")


def three_with_column_renamed_calls_in_a_row() -> None:
    df.withColumnRenamed("a", "x").withColumnRenamed("b", "y").withColumnRenamed("c", "z")


def with_column_renamed_chain_assigned() -> None:
    result = df.withColumnRenamed("first_name", "forename").withColumnRenamed("last_name", "surname")


def with_column_renamed_chain_after_filter() -> None:
    df.filter(col("active")).withColumnRenamed("a", "x").withColumnRenamed("b", "y")


def with_column_renamed_chain_inside_return() -> None:
    return df.withColumnRenamed("a", "x").withColumnRenamed("b", "y").withColumnRenamed("c", "z")


def with_column_renamed_chain_followed_by_select() -> None:
    df.withColumnRenamed("a", "x").withColumnRenamed("b", "y").select("x", "y")


def leaves_function_unchanged(x: int, y: int) -> int:
    return x + y
