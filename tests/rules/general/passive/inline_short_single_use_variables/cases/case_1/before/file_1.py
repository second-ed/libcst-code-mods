def single_use_variable_is_inlined() -> None:
    a = "something"
    b = fn(a=a)


def multi_use_variable_is_unchanged() -> None:
    a = "something"
    b = super_long_function_name_that_is_longer_than_the_limit(a=a)
    c = fn2(b, a=a)


def variable_is_unchanged_if_variable_value_is_too_long() -> None:
    z = [some_long_function_name(x) for x in y if a]
    b = fn(z=z)


def variable_with_multiple_attribute_uses_is_unchanged() -> None:
    root = Path("src")
    root.glob("*.py")
    root.rglob("*.py")


def variable_used_in_fstring_is_inlined_if_it_includes_quote_chars_they_are_changed_to_avoid_syntax_errors() -> None:
    isinstance_checks_str = ", ".join(isinstance_checks)
    message = f"{isinstance_checks_str}"


def variable_used_in_subscript_is_inlined() -> None:
    block_body = list(updated_node.body.body)
    last = block_body[-1]


def variable_used_as_method_receiver_is_inlined() -> None:
    cond = extracted["if_cond"]
    new_cond = cond.visit(transformer)


def variable_used_as_attribute_is_inlined() -> None:
    original_assign = original_node.body[0]
    value = original_assign.value


def variable_used_in_attribute_update_is_inlined() -> None:
    updated_assign = updated_node.body[0]
    result = updated_assign.with_changes(value=result)


def single_use_list_comp_is_inlined() -> None:
    a = [f(x) for x in y]
    b = fn(a=a)
