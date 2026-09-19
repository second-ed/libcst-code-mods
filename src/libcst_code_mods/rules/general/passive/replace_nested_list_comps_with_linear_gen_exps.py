import attrs

from libcst_code_mods.core.base_cst_transformer import BaseCstTransformer
from libcst_code_mods.core.base_cst_visitor import BaseCstVisitor
from libcst_code_mods.core.refactoring_rule import RefactoringRule
from libcst_code_mods.rules._rule_mapping import register_rule, register_rule_transformer, register_rule_visitor


@register_rule
@attrs.define(frozen=True)
class ReplaceNestedListCompsWithLinearGenExps(RefactoringRule):
    """Examples:

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def nested_comps_with_depth_1(y: list) -> None:
                z = [fn_1(a) for a in y]

        Post-transformer:

        .. code-block:: python

            def nested_comps_with_depth_1(y: list) -> None:
                z = list(map(fn_1, y))

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def nested_comps_with_depth_1_and_filters_1(y: list) -> None:
                z = [fn_1(a) for a in y if fil_1(a)]

        Post-transformer:

        .. code-block:: python

            def nested_comps_with_depth_1_and_filters_1(y: list) -> None:
                __s = filter(fil_1, y)
                z = list(map(fn_1, __s))

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def nested_comps_with_depth_2(y: list) -> None:
                z = [fn_2(b) for b in [fn_1(a) for a in y]]

        Post-transformer:

        .. code-block:: python

            def nested_comps_with_depth_2(y: list) -> None:
                __s = map(fn_1, y)
                z = list(map(fn_2, __s))

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def nested_comps_with_depth_2_and_filters_1(y: list) -> None:
                z = [fn_2(b) for b in [fn_1(a) for a in y if fil_1(a)]]

        Post-transformer:

        .. code-block:: python

            def nested_comps_with_depth_2_and_filters_1(y: list) -> None:
                __s = filter(fil_1, y)
                __s = map(fn_1, __s)
                z = list(map(fn_2, __s))

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def nested_comps_with_depth_2_and_filters_2(y: list) -> None:
                z = [fn_2(b) for b in [fn_1(a) for a in y if fil_1(a)] if fil_2(b)]

        Post-transformer:

        .. code-block:: python

            def nested_comps_with_depth_2_and_filters_2(y: list) -> None:
                __s = filter(fil_1, y)
                __s = map(fn_1, __s)
                __s = filter(fil_2, __s)
                z = list(map(fn_2, __s))

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def nested_comps_with_depth_3(y: list) -> None:
                z = [fn_3(c) for c in [fn_2(b) for b in [fn_1(a) for a in y]]]

        Post-transformer:

        .. code-block:: python

            def nested_comps_with_depth_3(y: list) -> None:
                __s = map(fn_1, y)
                __s = map(fn_2, __s)
                z = list(map(fn_3, __s))

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def nested_comps_with_depth_3_and_filters_1(y: list) -> None:
                z = [fn_3(c) for c in [fn_2(b) for b in [fn_1(a) for a in y if fil_1(a)]]]

        Post-transformer:

        .. code-block:: python

            def nested_comps_with_depth_3_and_filters_1(y: list) -> None:
                __s = filter(fil_1, y)
                __s = map(fn_1, __s)
                __s = map(fn_2, __s)
                z = list(map(fn_3, __s))

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def nested_comps_with_depth_3_and_filters_2(y: list) -> None:
                z = [fn_3(c) for c in [fn_2(b) for b in [fn_1(a) for a in y if fil_1(a)] if fil_2(b)]]

        Post-transformer:

        .. code-block:: python

            def nested_comps_with_depth_3_and_filters_2(y: list) -> None:
                __s = filter(fil_1, y)
                __s = map(fn_1, __s)
                __s = filter(fil_2, __s)
                __s = map(fn_2, __s)
                z = list(map(fn_3, __s))

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def nested_comps_with_depth_3_and_filters_3(y: list) -> None:
                z = [fn_3(c) for c in [fn_2(b) for b in [fn_1(a) for a in y if fil_1(a)] if fil_2(b)] if fil_3(c)]

        Post-transformer:

        .. code-block:: python

            def nested_comps_with_depth_3_and_filters_3(y: list) -> None:
                __s = filter(fil_1, y)
                __s = map(fn_1, __s)
                __s = filter(fil_2, __s)
                __s = map(fn_2, __s)
                __s = filter(fil_3, __s)
                z = list(map(fn_3, __s))

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def nested_comps_with_depth_4(y: list) -> None:
                z = [fn_4(d) for d in [fn_3(c) for c in [fn_2(b) for b in [fn_1(a) for a in y]]]]

        Post-transformer:

        .. code-block:: python

            def nested_comps_with_depth_4(y: list) -> None:
                __s = map(fn_1, y)
                __s = map(fn_2, __s)
                __s = map(fn_3, __s)
                z = list(map(fn_4, __s))

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def nested_comps_with_depth_4_and_filters_1(y: list) -> None:
                z = [fn_4(d) for d in [fn_3(c) for c in [fn_2(b) for b in [fn_1(a) for a in y if fil_1(a)]]]]

        Post-transformer:

        .. code-block:: python

            def nested_comps_with_depth_4_and_filters_1(y: list) -> None:
                __s = filter(fil_1, y)
                __s = map(fn_1, __s)
                __s = map(fn_2, __s)
                __s = map(fn_3, __s)
                z = list(map(fn_4, __s))

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def nested_comps_with_depth_4_and_filters_2(y: list) -> None:
                z = [fn_4(d) for d in [fn_3(c) for c in [fn_2(b) for b in [fn_1(a) for a in y if fil_1(a)] if fil_2(b)]]]

        Post-transformer:

        .. code-block:: python

            def nested_comps_with_depth_4_and_filters_2(y: list) -> None:
                __s = filter(fil_1, y)
                __s = map(fn_1, __s)
                __s = filter(fil_2, __s)
                __s = map(fn_2, __s)
                __s = map(fn_3, __s)
                z = list(map(fn_4, __s))

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def nested_comps_with_depth_4_and_filters_3(y: list) -> None:
                z = [
                    fn_4(d) for d in [fn_3(c) for c in [fn_2(b) for b in [fn_1(a) for a in y if fil_1(a)] if fil_2(b)] if fil_3(c)]
                ]

        Post-transformer:

        .. code-block:: python

            def nested_comps_with_depth_4_and_filters_3(y: list) -> None:
                __s = filter(fil_1, y)
                __s = map(fn_1, __s)
                __s = filter(fil_2, __s)
                __s = map(fn_2, __s)
                __s = filter(fil_3, __s)
                __s = map(fn_3, __s)
                z = list(map(fn_4, __s))

        Case
        ----

        Pre-transformer:

        .. code-block:: python

            def nested_comps_with_depth_4_and_filters_4(y: list) -> None:
                z = [
                    fn_4(d)
                    for d in [fn_3(c) for c in [fn_2(b) for b in [fn_1(a) for a in y if fil_1(a)] if fil_2(b)] if fil_3(c)]
                    if fil_4(d)
                ]

        Post-transformer:

        .. code-block:: python

            def nested_comps_with_depth_4_and_filters_4(y: list) -> None:
                __s = filter(fil_1, y)
                __s = map(fn_1, __s)
                __s = filter(fil_2, __s)
                __s = map(fn_2, __s)
                __s = filter(fil_3, __s)
                __s = map(fn_3, __s)
                __s = filter(fil_4, __s)
                z = list(map(fn_4, __s))
    ---
    """


@register_rule_visitor(ReplaceNestedListCompsWithLinearGenExps)
@attrs.define
class ReplaceNestedListCompsWithLinearGenExpsVisitor(BaseCstVisitor):
    pass


@register_rule_transformer(ReplaceNestedListCompsWithLinearGenExps)
@attrs.define
class ReplaceNestedListCompsWithLinearGenExpsTransformer(BaseCstTransformer):
    pass
