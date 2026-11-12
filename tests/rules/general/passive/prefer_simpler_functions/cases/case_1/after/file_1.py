def function_with_two_decisions() -> None:
    if condition_a:
        pass

    for item in items:
        pass


def function_with_three_decisions() -> None:
    if condition_a:
        pass

    for item in items:
        pass

    while condition_b:
        pass


def function_with_three_if_statements() -> None:
    if condition_a:
        pass
    if condition_b:
        pass
    if condition_c:
        pass


def function_with_three_for_statements() -> None:
    for item in items_a:
        pass
    for item in items_b:
        pass
    for item in items_c:
        pass


def function_with_three_while_statements() -> None:
    while condition_a:
        pass
    while condition_b:
        pass
    while condition_c:
        pass


def function_with_four_if_expressions() -> None:
    a = 1 if condition_a else 0
    b = 1 if condition_b else 0
    c = 1 if condition_c else 0
    d = 1 if condition_d else 0


def function_with_four_except_handlers() -> None:
    try:
        pass
    except ValueError:
        pass

    try:
        pass
    except TypeError:
        pass

    try:
        pass
    except RuntimeError:
        pass

    try:
        pass
    except Exception:
        pass


def function_with_match_cases() -> None:
    match value:
        case 1:
            pass
    match value:
        case 2:
            pass
    match value:
        case 3:
            pass
    match value:
        case 4:
            pass


def triggers_for_single_match_with_multiple_cases() -> None:
    match value:
        case 1:
            pass
        case 2:
            pass
        case 3:
            pass
        case 4:
            pass


def function_with_multiple_ands_and_ors() -> None:
    thing = (a and b and (c or d)) or e
