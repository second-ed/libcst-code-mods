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
    original_node: cst.For,  # noqa: ARG001
    updated_node: cst.For,
    call_matcher: m.BaseMatcherNode,
    new_fn_name: str,
) -> cst.For | cst.Assign:
    extracted_nodes = m.extract(updated_node, call_matcher)

    if extracted_nodes is None:
        return updated_node

    name = extracted_nodes["name"]
    expr = extracted_nodes["expr"]
    loop = extracted_nodes["loop"]
    iterable = extracted_nodes["iterable"]
    target = extracted_nodes["target"]

    dict_comp = cst.DictComp(key=name, value=expr, for_in=cst.CompFor(target=loop, iter=iterable))

    new_call = cst.Call(func=cst.Attribute(value=target, attr=cst.Name(new_fn_name)), args=[cst.Arg(value=dict_comp)])
    return cst.SimpleStatementLine(body=[cst.Assign(targets=[cst.AssignTarget(target=target)], value=new_call)])
