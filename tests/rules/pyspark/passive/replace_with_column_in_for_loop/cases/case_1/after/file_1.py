def should_update_this_function() -> None:
    df = df.withColumns({col: lit(0) for col in ["a", "b", "c"]})


def unrelated_for_loop() -> None:
    for i in range(10):
        print(i)
