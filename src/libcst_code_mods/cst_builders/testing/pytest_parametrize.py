from collections.abc import Iterable

import libcst as cst

from libcst_code_mods.cst_builders.primitives import CST_TYPES
from libcst_code_mods.cst_builders.primitives.collections import cst_list, cst_tuple
from libcst_code_mods.cst_builders.primitives.declarations import cst_kwarg, cst_param, cst_stmt, with_block
from libcst_code_mods.cst_builders.primitives.expressions import cst_call
from libcst_code_mods.cst_builders.primitives.literals import cst_str


def create_test_fn(
    name: str, params: dict[str, str], return_annot: str, raises: list[str] | None = None
) -> cst.FunctionDef:
    raises = raises or []
    expected_result = {"expected_result": return_annot}
    combined_params = {**params, **expected_result}
    assertion = cst_stmt(
        cst.Assert(
            test=cst.Comparison(
                left=cst_call(name, [cst.Name(parameter) for parameter in params]),
                comparisons=[cst.ComparisonTarget(operator=cst.Equal(), comparator=cst.Name("expected_result"))],
            )
        )
    )

    if raises:
        assertion = with_block("expected_context", [assertion])
        combined_params["expected_context"] = "ContextManager"

    return cst.FunctionDef(
        name=cst.Name(f"test_{name}"),
        params=cst.Parameters(
            params=[cst_param(parameter, annotation) for parameter, annotation in combined_params.items()]
        ),
        body=cst.IndentedBlock(body=[assertion]),
        decorators=[_pytest_parametrize(combined_params, raises)],
        returns=cst.Annotation(cst.Name("None")),
    )


def _pytest_parametrize(params: dict[str, str], raises: list[str] | None = None) -> cst.Decorator:
    raises = raises or []
    normal_case = _pytest_param((_parse_value(value) for value in params.values()), "given..., when..., then...")
    raising_cases = [
        _pytest_param(
            [
                *(_parse_value(value) for key, value in params.items() if key != "expected_context"),
                cst_call("pytest.raises", [cst.Name(error)]),
            ],
            f"given..., when..., then should raise {error}",
        )
        for error in raises
    ]

    argnames = cst_tuple([cst_str(p) for p in params])
    argvalues = cst_list([normal_case, *raising_cases])
    return cst.Decorator(cst_call("pytest.mark.parametrize", [argnames, argvalues]))


def _parse_value(value: str) -> cst.BaseExpression:
    return CST_TYPES.get(value) or cst.parse_expression(value)


def _pytest_param(values: Iterable[cst.BaseExpression], case_id: str) -> cst.Call:
    return cst_call("pytest.param", [*values, cst_kwarg("id", cst_str(case_id))])
