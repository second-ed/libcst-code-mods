def should_update_this_function() -> None:
    for col in ["a", "b", "c"]:
        df = df.withColumn(col, lit(0))


def unrelated_for_loop() -> None:
    for i in range(10):
        print(i)


def correctly_updates_iterating_over_mapping() -> None:
    for col, expr in mapping.items():
        df = df.withColumn(col, expr)
