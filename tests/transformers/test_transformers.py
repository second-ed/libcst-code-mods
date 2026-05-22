from pathlib import Path

import pytest

from libcst_code_mods.constants import REPO_ROOT
from libcst_code_mods.single_file_transformers.convert_function_signature import ConvertFunctionSignature
from libcst_code_mods.single_file_transformers.rename_variable_of_type import RenameVariableOfType
from libcst_code_mods.single_file_transformers.reorder_params import ReorderParams
from libcst_code_mods.single_file_transformers.replace_param_type_hint import ReplaceParamTypeHint
from libcst_code_mods.single_file_transformers.replace_return_type_hint import ReplaceReturnTypeHint
from libcst_code_mods.transform import transform_code


@pytest.mark.parametrize(
    ("usecase_name", "case_name", "transformers"),
    [
        pytest.param(
            "convert_function_signature",
            "case_1",
            [ConvertFunctionSignature("add", "new_sum", {0: "a", 1: "b"}, {"a": "value_1", "b": "value_2"})],
        ),
        pytest.param(
            "rename_variables_of_same_type", "case_1", [RenameVariableOfType("CustomLoggingHandler", "custom_handler")]
        ),
        pytest.param("replace_param_type_hint", "case_1", [ReplaceParamTypeHint("int", "str")]),
        pytest.param(
            "replace_param_type_hint",
            "case_2",
            [ReplaceParamTypeHint("int", "str", function_name="not_present_function")],
        ),
        pytest.param("replace_return_type_hint", "case_1", [ReplaceReturnTypeHint("int", "float")]),
        pytest.param(
            "combinations",
            "case_1",
            [
                ReplaceParamTypeHint("int", "float", function_name="func_single_line"),
                ReplaceReturnTypeHint("int", "float", function_name="func_single_line"),
            ],
        ),
        pytest.param("reorder_params", "case_1", [ReorderParams("func", ["c", "b", "a"])]),
    ],
)
def test_transformers(usecase_name, case_name, transformers) -> None:
    usecase_root = f"{REPO_ROOT}/tests/test_transformer_cases/{usecase_name}/{case_name}"
    before_path = f"{usecase_root}/before.py"
    after_path = f"{usecase_root}/after.py"

    res = transform_code(usecase_root, before_path, transformers)

    assert res.splitlines() == Path(after_path).read_text().splitlines()
