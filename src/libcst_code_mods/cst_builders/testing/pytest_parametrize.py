import libcst as cst

from libcst_code_mods.cst_builders.primitives import CST_TYPES
from libcst_code_mods.cst_builders.primitives.collections import cst_list, cst_tuple
from libcst_code_mods.cst_builders.primitives.expressions import cst_call
from libcst_code_mods.cst_builders.primitives.literals import cst_str


def pytest_parametrize(params: dict[str, str]) -> cst.Decorator:
    argnames = cst_tuple([cst_str(p) for p in params])
    argvalues = cst_list(
        [cst_call("pytest.param", [(CST_TYPES.get(v) or cst.parse_expression(v)) for v in params.values()])]
    )
    return cst.Decorator(cst_call("pytest.mark.parametrize", [argnames, argvalues]))
