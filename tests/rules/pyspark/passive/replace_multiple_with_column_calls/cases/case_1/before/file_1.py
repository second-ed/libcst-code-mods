def two_with_column_calls_in_a_row() -> None:
    df.withColumn("a", lit(1)).withColumn("b", col("blah"))
