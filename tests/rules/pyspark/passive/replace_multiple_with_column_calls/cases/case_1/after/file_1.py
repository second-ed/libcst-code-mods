def one_with_column_call_unchanged() -> None:
    df.withColumn("a", lit(1))


def two_with_column_calls_in_a_row() -> None:
    df.withColumns({"a": lit(1), "b": col("blah")})


def three_with_column_calls_in_a_row() -> None:
    df.withColumns({"a": lit(1), "b": col("blah"), "c": lit(3)})


def with_column_chain_assigned() -> None:
    result = df.withColumns({"a": lit(1), "b": col("blah"), "c": upper(col("name"))})


def with_column_chain_after_filter() -> None:
    df.filter(col("active")).withColumns({"a": lit(1), "b": col("blah")})


def with_column_chain_inside_return() -> None:
    return df.withColumns({"a": lit(1), "b": col("blah"), "c": concat(col("x"), col("y"))})


def with_column_chain_followed_by_select() -> None:
    df.withColumns({"a": lit(1), "b": col("blah")}).select("a", "b")


def leaves_function_unchanged(x: int, y: int) -> int:
    return x + y
