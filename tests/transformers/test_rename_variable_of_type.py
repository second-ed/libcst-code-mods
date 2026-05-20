from pathlib import Path

import libcst.matchers as m
import pytest

import libcst_code_mods.matchers as mat
from libcst_code_mods.constants import REPO_ROOT
from libcst_code_mods.transform import transform_code
from libcst_code_mods.transformers.rename_variable_of_type import RenameVariableOfType


@pytest.mark.parametrize(
    ("usecase_name", "case_name", "transformers"),
    [
        pytest.param(
            "rename_variables_of_same_type",
            "case_1",
            [
                RenameVariableOfType(
                    (
                        mat.assignment_has_type_hint(m.Name("CustomLoggingHandler"))
                        | mat.param_has_type_hint(m.Name("CustomLoggingHandler"))
                    ),
                    "CustomLoggingHandler",
                    "custom_handler",
                )
            ],
        ),
    ],
)
def test_rename_variables_of_same_type(usecase_name, case_name, transformers):
    usecase_root = f"{REPO_ROOT}/tests/test_transformer_cases/{usecase_name}/{case_name}"
    before_path = f"{usecase_root}/before.py"
    after_path = f"{usecase_root}/after.py"

    res = transform_code(usecase_root, before_path, transformers)

    assert res.splitlines() == Path(after_path).read_text().splitlines()
