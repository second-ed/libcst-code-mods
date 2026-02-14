import libcst.matchers as m
import pytest

import libcst_code_mods.matchers as mat
from libcst_code_mods.apply import apply_code_mod
from libcst_code_mods.transformers import RenameVariableOfType


@pytest.mark.parametrize(
    "fixture_get_usecase_case",
    [
        "rename_variables_of_same_type",
    ],
    indirect=True,
)
def test_rename_variables_of_same_type(fixture_get_usecase_case):
    before, after = fixture_get_usecase_case

    matcher = mat.assignment_has_type_hint(m.Name("CustomLoggingHandler")) | mat.param_has_type_hint(
        m.Name("CustomLoggingHandler")
    )

    assert (
        apply_code_mod(before, matcher, RenameVariableOfType("CustomLoggingHandler", "custom_handler")).splitlines()
        == after.splitlines()
    )
