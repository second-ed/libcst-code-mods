def should_update_this_function() -> None:
    df = df.withColumnsRenamed({col: f"{col}_new" for col in ["a", "b", "c"]})


def unrelated_for_loop() -> None:
    for i in range(10):
        print(i)


def correctly_updates_iterating_over_mapping() -> None:
    df = df.withColumnsRenamed({old: new for old, new in mapping.items()})


def ignores_if_line_before_with_column_call() -> None:
    for old, new in mapping.items():
        print(old)
        df = df.withColumnRenamed(old, new)


def ignores_if_line_after_with_column_call() -> None:
    for old, new in mapping.items():
        df = df.withColumnRenamed(old, new)
        print(old)
