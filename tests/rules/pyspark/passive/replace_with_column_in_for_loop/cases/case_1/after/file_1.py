def should_update_this_function() -> None:
    df = df.withColumns({col: lit(0) for col in ["a", "b", "c"]})


def unrelated_for_loop() -> None:
    for i in range(10):
        print(i)


def correctly_updates_iterating_over_mapping() -> None:
    df = df.withColumns({col: expr for col, expr in mapping.items()})


def ignores_if_line_before_with_column_call() -> None:
    for col, expr in mapping.items():
        print(col)
        df = df.withColumn(col, expr)


def ignores_if_line_after_with_column_call() -> None:
    for col, expr in mapping.items():
        df = df.withColumn(col, expr)
        print(col)
