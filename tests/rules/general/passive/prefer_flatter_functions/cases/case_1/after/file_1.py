def function_with_four_nested_if_blocks(a: bool, b: bool, c: bool, d: bool) -> None:
    if a:
        if b:
            if c:
                if d:
                    pass


def function_with_four_sibling_if_blocks(a: bool, b: bool, c: bool, d: bool) -> None:
    if a:
        pass
    if b:
        pass
    if c:
        pass
    if d:
        pass


def function_with_nested_function_and_one_outer_if(a: bool) -> None:
    if a:
        pass

    def nested_function_with_one_if_block(b: bool) -> None:
        if b:
            pass


def function_with_nested_function_containing_four_nested_if_blocks() -> None:
    def nested_function_with_four_nested_if_blocks(a: bool, b: bool, c: bool, d: bool) -> None:
        if a:
            if b:
                if c:
                    if d:
                        pass
