def two_with_column_renamed_calls_in_a_row() -> None:
    df.withColumnsRenamed({"a": "x", "b": "y"})


def three_with_column_renamed_calls_in_a_row() -> None:
    df.withColumnsRenamed({"a": "x", "b": "y", "c": "z"})


def with_column_renamed_chain_assigned() -> None:
    result = df.withColumnsRenamed({"first_name": "forename", "last_name": "surname"})


def with_column_renamed_chain_after_filter() -> None:
    df.filter(col("active")).withColumnRenamed({"a": "x", "b": "y"})


def with_column_renamed_chain_inside_return() -> None:
    return df.withColumnRenamed({"a": "x", "b": "y", "c": "z"})


def with_column_renamed_chain_followed_by_select() -> None:
    df.withColumnRenamed({"a": "x", "b": "y"}).select("x", "y")


def leaves_function_unchanged(x: int, y: int) -> int:
    return x + y
