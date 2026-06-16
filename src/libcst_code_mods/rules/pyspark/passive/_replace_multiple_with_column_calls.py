import libcst as cst
import libcst.matchers as m

from libcst_code_mods.core.base_cst_transformer import BaseCstTransformer


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

    columns.reverse()

    return cst.Call(
        func=cst.Attribute(value=current, attr=cst.Name(new_fn_name)),
        args=[cst.Arg(value=cst.Dict(elements=[cst.DictElement(key=name, value=expr) for name, expr in columns]))],
    )
