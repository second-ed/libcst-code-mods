from pathlib import Path

import pytest

from libcst_code_mods.constants import REPO_ROOT
from libcst_code_mods.transform import transform_code
from libcst_code_mods.transformers.replace_return_type_hint import ReplaceReturnTypeHint


@pytest.mark.parametrize(
    ("usecase_name", "case_name", "transformers"),
    [pytest.param("replace_return_type_hint", "case_1", [ReplaceReturnTypeHint(None, "int", "float")])],
)
def test_replace_return_type_hint(usecase_name, case_name, transformers):
    usecase_root = f"{REPO_ROOT}/tests/test_transformer_cases/{usecase_name}/{case_name}"
    before_path = f"{usecase_root}/before.py"
    after_path = f"{usecase_root}/after.py"

    res = transform_code(usecase_root, before_path, transformers)

    assert res.splitlines() == Path(after_path).read_text().splitlines()
