from pathlib import Path

import pytest

from libcst_code_mods.constants import REPO_ROOT
from libcst_code_mods.rules._rule_mapping import RULE_MAPPING
from libcst_code_mods.rules.convert_function_signature import ConvertFunctionSignature
from libcst_code_mods.transform_v2 import transform_code


@pytest.mark.parametrize(
    ("usecase_name", "case_name", "transformers"),
    [
        pytest.param(
            "convert_function_signature",
            "case_1",
            [ConvertFunctionSignature("add", "new_sum", {"a": "value_1", "b": "value_2"})],
        )
    ],
)
def test_transformers(usecase_name, case_name, transformers) -> None:
    usecase_root = f"{REPO_ROOT}/tests/test_transformer_cases/{usecase_name}/{case_name}"
    before_path = f"{usecase_root}/before.py"
    after_path = f"{usecase_root}/after.py"

    res = transform_code(usecase_root, before_path, transformers, RULE_MAPPING)

    assert res.splitlines() == Path(after_path).read_text().splitlines()
