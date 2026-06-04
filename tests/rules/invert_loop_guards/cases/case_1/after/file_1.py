def simple_loop_with_if_else() -> None:
    for i in range(10):
        if i % 2 != 0:
            print(f"{i} is odd")
            continue
        print(f"{i} is even")


def loop_with_extra_statements_and_if_else() -> None:
    for i in range(10):
        x = 2
        y = 0
        y += x
        if i % 2 != 0:
            print(f"{i} is odd")
            continue
        print(f"{i} is even")
