from pathlib import Path

import pytest

from libcst_code_mods.constants import REPO_ROOT
from libcst_code_mods.rules._rule_mapping import RULE_MAPPING
from libcst_code_mods.rules.convert_function_signature import ConvertFunctionSignature
from libcst_code_mods.transform_v2 import multi_file_refactor
from libcst_code_mods.utils import diff_code_maps, paths_to_code_map


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
def test_convert_function_signature(usecase_name, case_name, transformers) -> None:
    usecase_root = f"{REPO_ROOT}/tests/rules/{usecase_name}/cases/{case_name}"
    before_paths = list(Path(f"{usecase_root}/before").rglob("**/*.py"))
    after_paths = list(Path(f"{usecase_root}/after").rglob("**/*.py"))

    refactored_code = multi_file_refactor(usecase_root, before_paths, transformers, RULE_MAPPING)

    assert diff_code_maps(paths_to_code_map(after_paths), refactored_code) == {}
