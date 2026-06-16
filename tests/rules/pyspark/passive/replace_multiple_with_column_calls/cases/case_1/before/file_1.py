def two_with_column_calls_in_a_row() -> None:
    df.withColumn("a", lit(1)).withColumn("b", col("blah"))


def three_with_column_calls_in_a_row() -> None:
    df.withColumn("a", lit(1)).withColumn("b", col("blah")).withColumn("c", lit(3))


def with_column_chain_assigned() -> None:
    result = df.withColumn("a", lit(1)).withColumn("b", col("blah")).withColumn("c", upper(col("name")))


def with_column_chain_after_filter() -> None:
    df.filter(col("active")).withColumn("a", lit(1)).withColumn("b", col("blah"))


def with_column_chain_inside_return() -> None:
    return df.withColumn("a", lit(1)).withColumn("b", col("blah")).withColumn("c", concat(col("x"), col("y")))


def with_column_chain_followed_by_select() -> None:
    df.withColumn("a", lit(1)).withColumn("b", col("blah")).select("a", "b")


def leaves_function_unchanged(x: int, y: int) -> int:
    return x + y
