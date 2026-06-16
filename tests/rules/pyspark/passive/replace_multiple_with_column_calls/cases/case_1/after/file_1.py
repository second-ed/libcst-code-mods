def two_with_column_calls_in_a_row() -> None:
    df.withColumns({"a": lit(1), "b": col("blah")})
