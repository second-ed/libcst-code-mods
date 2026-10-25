import libcst as cst


def cst_param(name: str, annot: str | None = None, default: cst.BaseExpression | None = None) -> cst.Param:
    annotation = cst.Annotation(cst.Name(annot)) if annot is not None else None
    return cst.Param(cst.Name(name), annotation=annotation, default=default)


def cst_kwarg(name: str, value: cst.BaseExpression) -> cst.Arg:
    return cst.Arg(keyword=cst.Name(name), value=value)


def cst_stmt(stmt: cst.BaseSmallStatement) -> cst.SimpleStatementLine:
    return cst.SimpleStatementLine([stmt])


def with_block(name: str, stmts: list[cst.SimpleStatementLine]) -> cst.With:
    return cst.With([cst.WithItem(cst.Name(name))], cst.IndentedBlock(stmts))
