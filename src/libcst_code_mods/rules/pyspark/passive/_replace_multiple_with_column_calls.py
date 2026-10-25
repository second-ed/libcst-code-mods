import libcst as cst
import libcst.matchers as m

from libcst_code_mods.core.base_cst_transformer import BaseCstTransformer
from libcst_code_mods.cst_builders.primitives.collections import cst_dict
from libcst_code_mods.cst_builders.primitives.expressions import cst_call


def update_multiple_with_column_calls(  # noqa: PLR0913
    cls: BaseCstTransformer,
    original_node: cst.Call,
    updated_node: cst.Call,
    call_matcher: m.BaseMatcherNode,
    attr_matcher: m.BaseMatcherNode,
    new_fn_name: str,
) -> cst.Call:
    if not m.matches(updated_node, call_matcher):
        return updated_node

    parent = cls.get_metadata(cst.metadata.ParentNodeProvider, original_node)

    # Only transform the outermost call in a chain.
    if m.matches(parent, attr_matcher):
        return updated_node

    columns = []
    current = updated_node

    while m.matches(current, call_matcher) and len(current.args) >= 2:  # noqa: PLR2004
        columns.append((current.args[0].value, current.args[1].value))
        current = current.func.value

    if len(columns) == 1:
        return updated_node

    columns.reverse()

    return cst_call(
        new_fn_name, [cst_dict([cst.DictElement(key=name, value=expr) for name, expr in columns])]
    ).with_changes(func=cst.Attribute(value=current, attr=cst.Name(new_fn_name)))
