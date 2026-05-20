from pathlib import Path

import libcst.matchers as m
import pytest

from libcst_code_mods.constants import REPO_ROOT
from libcst_code_mods.transform import transform_code
from libcst_code_mods.transformers.convert_function_signature import ConvertFunctionSignature


@pytest.mark.parametrize(
    ("usecase_name", "case_name", "transformers"),
    [
        pytest.param(
            "convert_function_signature",
            "case_1",
            [
                ConvertFunctionSignature(
                    m.Call(m.Name(value="add")), "new_sum", {0: "a", 1: "b"}, {"a": "value_1", "b": "value_2"}
                )
            ],
        ),
    ],
)
def test_to_new_function(usecase_name, case_name, transformers) -> None:
    usecase_root = f"{REPO_ROOT}/tests/test_transformer_cases/{usecase_name}/{case_name}"
    before_path = f"{usecase_root}/before.py"
    after_path = f"{usecase_root}/after.py"

    res = transform_code(usecase_root, before_path, transformers)

    assert res.splitlines() == Path(after_path).read_text().splitlines()
