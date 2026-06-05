def no_op_because_does_not_end_with_if_else() -> None:
    for i in range(10):
        if i % 2 == 0:
            print(f"{i} is even")
        else:
            print(f"{i} is odd")
        x = 2
        y = 0
        y += x
