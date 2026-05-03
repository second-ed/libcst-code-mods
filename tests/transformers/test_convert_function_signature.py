from pathlib import Path

import libcst.matchers as m
import pytest

from libcst_code_mods.apply import apply_code_mod
from libcst_code_mods.constants import REPO_ROOT
from libcst_code_mods.transformers.convert_function_signature import ConvertFunctionSignature


@pytest.mark.parametrize(
    ("usecase_name", "case_name", "matcher", "transformer"),
    [
        pytest.param(
            "convert_function_signature",
            "case_1",
            (m.Call()),
            ConvertFunctionSignature("new_sum", {0: "a", 1: "b"}, {"a": "value_1", "b": "value_2"}),
        ),
    ],
)
def test_to_new_function(usecase_name, case_name, matcher, transformer) -> None:
    usecase_root = f"{REPO_ROOT}/tests/test_transformer_cases/{usecase_name}/{case_name}"
    before_path = f"{usecase_root}/before.py"
    after_path = f"{usecase_root}/after.py"

    res = apply_code_mod(usecase_root, before_path, matcher, transformer)

    assert res.splitlines() == Path(after_path).read_text().splitlines()
