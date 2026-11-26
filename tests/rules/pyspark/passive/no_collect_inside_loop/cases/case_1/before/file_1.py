def some_function_does_not_trigger(df: DataFrame) -> None:
    df.drop("a").withColumn("b", lit("thing"))


def calls_collect_but_not_in_loop() -> None:
    df.collect()

    for i in range(10):
        print(i)


def calls_collect_in_loop() -> None:
    for i in range(10):
        df.withColumn("thing", lit(i)).collect()
