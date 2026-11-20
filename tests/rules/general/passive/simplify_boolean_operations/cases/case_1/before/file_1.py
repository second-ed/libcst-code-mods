identity_and = A and True
identity_or = A or False
domination_and = A and False
domination_or = A or True
idempotent_and = A and A
idempotent_or = A or A
complement_and = A and not A
complement_or = A or not A
absorption_or = A or (A and B)
absorption_and = A and (A or B)
double_negation = not not A
demorgan_and = not (A and B)
demorgan_or = not (A or B)
constant_not_true = not True
constant_not_false = not False

composite_identity_and_and_absorption_or = (A and True) and (A or (A and B))
composite_factor_and_or = (A and B) or (A and not B)
composite_factor_or_and = (A or B) and (A or not B)
composite_factor_and_or_common_right = (A and B) or (not A and B)
composite_factor_or_and_common_right = (A or B) and (not A or B)
flattened_composite_factor = (A and B and C) or (A and not B and C)

# more complex ones
composite_a = (A or B) and (A or C)
composite_b = A and B and (not B and C or A and C)
composite_c = (A or not B or not C) and (A or not B or C) and (A or B or not C)
