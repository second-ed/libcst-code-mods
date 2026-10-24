def should_ignore_this_function_with_repartition() -> None:
    df.repartition(4).write.parquet("./blah")


def should_ignore_this_function_with_coalesce() -> None:
    df.coalesce(4).write.parquet("./blah")


def identifies_single_partition_repartition() -> None:
    df.repartition(1).write.parquet("./blah")


def identifies_single_partition_coalesce() -> None:
    df.coalesce(1).write.parquet("./blah")
