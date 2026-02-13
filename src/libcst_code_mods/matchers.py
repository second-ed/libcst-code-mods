from enum import Enum

import libcst.matchers as m


class NodeMatcher(Enum):
    IS_FUNCTION = m.FunctionDef()
    IS_CLASS = m.ClassDef()
    RAISES_EXCEPTION = m.FunctionDef(
        body=m.IndentedBlock(
            body=m.OneOf(
                [
                    m.SimpleStatementLine(body=[m.Raise(exc=m.DoNotCare())]),
                    m.IndentedBlock(body=[m.Raise(exc=m.DoNotCare())]),
                ]
            )
        )
    )
    HAS_RETURN_TYPE = m.FunctionDef(returns=m.Annotation(annotation=m.DoNotCare()))
