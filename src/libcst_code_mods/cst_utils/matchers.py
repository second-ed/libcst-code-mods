import libcst.matchers as m

DOCSTRING = m.SimpleStatementLine([m.Expr(m.SimpleString())])
IMPORT_MATCHER = m.SimpleStatementLine([m.OneOf(m.Import(), m.ImportFrom())])
TRY_IMPORT_MATCHER = m.Try(m.IndentedBlock([m.AtLeastN(IMPORT_MATCHER, n=1)]))
GLOBAL_ASSIGNMENT = m.SimpleStatementLine([m.OneOf(m.Assign(), m.AnnAssign())])
