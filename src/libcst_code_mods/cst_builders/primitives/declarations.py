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


def cst_import(name: str, as_name: str | None = None) -> cst.SimpleStatementLine:
    cst_as_name = cst.AsName(cst.Name(as_name)) if as_name is not None else as_name
    return cst_stmt(cst.Import(names=[cst.ImportAlias(name=cst.Name(value=name), asname=cst_as_name)]))
