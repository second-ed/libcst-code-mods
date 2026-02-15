from pathlib import Path

import libcst.matchers as m
import pytest

import libcst_code_mods.matchers as mat
from libcst_code_mods.apply import apply_code_mod
from libcst_code_mods.constants import REPO_ROOT
from libcst_code_mods.transformers import RenameVariableOfType


@pytest.mark.parametrize(
    ("usecase_name", "matcher", "transformer"),
    [
        pytest.param(
            "rename_variables_of_same_type",
            (
                mat.assignment_has_type_hint(m.Name("CustomLoggingHandler"))
                | mat.param_has_type_hint(m.Name("CustomLoggingHandler"))
            ),
            RenameVariableOfType("CustomLoggingHandler", "custom_handler"),
        ),
    ],
)
def test_rename_variables_of_same_type(usecase_name, matcher, transformer):
    usecase_root = f"{REPO_ROOT}/tests/test_transformer_cases/{usecase_name}"
    before_path = f"{usecase_root}/before.py"
    after_path = f"{usecase_root}/after.py"

    res = apply_code_mod(usecase_root, before_path, matcher, transformer)

    assert res.splitlines() == Path(after_path).read_text().splitlines()
