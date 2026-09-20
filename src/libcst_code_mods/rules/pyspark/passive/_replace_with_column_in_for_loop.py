import libcst as cst
import libcst.matchers as m


def for_loop_matcher(fn_name: str) -> m.For:
    return m.For(
        target=m.SaveMatchedNode(m.DoNotCare(), "loop"),
        iter=m.SaveMatchedNode(m.DoNotCare(), "iterable"),
        body=m.IndentedBlock(
            body=[
                m.SimpleStatementLine(
                    body=[
                        m.Assign(
                            targets=[m.AssignTarget(target=m.SaveMatchedNode(m.Name(), "target"))],
                            value=m.Call(
                                func=m.Attribute(attr=m.Name(fn_name)),
                                args=[
                                    m.Arg(value=m.SaveMatchedNode(m.DoNotCare(), "name")),
                                    m.Arg(value=m.SaveMatchedNode(m.DoNotCare(), "expr")),
                                ],
                            ),
                        )
                    ]
                )
            ]
        ),
    )


def update_with_column_call_in_for_loop(
    _original_node: cst.For, updated_node: cst.For, call_matcher: m.BaseMatcherNode, new_fn_name: str
) -> cst.For | cst.Assign:

    if (extracted_nodes := m.extract(updated_node, call_matcher)) is None:
        return updated_node
    target = extracted_nodes["target"]

    dict_comp = cst.DictComp(
        key=extracted_nodes["name"],
        value=extracted_nodes["expr"],
        for_in=cst.CompFor(target=extracted_nodes["loop"], iter=extracted_nodes["iterable"]),
    )

    new_call = cst.Call(func=cst.Attribute(value=target, attr=cst.Name(new_fn_name)), args=[cst.Arg(value=dict_comp)])
    return cst.SimpleStatementLine(body=[cst.Assign(targets=[cst.AssignTarget(target=target)], value=new_call)])
