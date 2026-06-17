from pathlib import Path

import pytest

from libcst_code_mods.rules._rule_mapping import RULE_MAPPING
from libcst_code_mods.rules.general.active.convert_function_signature import ConvertFunctionSignature
from libcst_code_mods.engine import multi_file_refactor
from tests.conftest import code_map_to_rows, diff_code_lfs, paths_to_rows, rows_to_lf


PARENT = Path(__file__).parent


@pytest.mark.parametrize(
    ("case_name", "transformers"),
    [pytest.param("case_1", [ConvertFunctionSignature("add", "new_sum", {"a": "value_1", "b": "value_2"})])],
)
def test_convert_function_signature(case_name, transformers) -> None:
    usecase_root = f"{PARENT}/cases/{case_name}"
    before_paths = list(Path(f"{usecase_root}/before").rglob("**/*.py"))
    after_paths = list(Path(f"{usecase_root}/after").rglob("**/*.py"))

    refactored_code = multi_file_refactor(usecase_root, before_paths, transformers, RULE_MAPPING)
    assert refactored_code
    assert (
        diff_code_lfs(
            rows_to_lf(paths_to_rows(after_paths, "expected"), usecase_root),
            rows_to_lf(code_map_to_rows(refactored_code, "actual"), usecase_root),
        )
        == {}
    )
