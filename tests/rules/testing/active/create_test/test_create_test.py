from pathlib import Path

import pytest

from libcst_code_mods.rules._rule_mapping import RULE_MAPPING
from libcst_code_mods.rules.testing.active.create_test import CreateTest
from libcst_code_mods.engine import multi_file_refactor
from tests.conftest import code_map_to_rows, diff_code_lfs, paths_to_rows, rows_to_lf


PARENT = Path(__file__).parent


@pytest.mark.skip
@pytest.mark.parametrize(
    ("case_name", "transformers", "expected_diagnostics"),
    [
        pytest.param(
            "case_1", [CreateTest(["add", "div"])], [], id="should create the test file if it doesn't already exist"
        ),
        pytest.param(
            "case_2",
            [CreateTest(["add", "div"])],
            [],
            id="should only create tests for functions that don't already have tests",
        ),
        pytest.param(
            "case_2",
            [CreateTest(["add"])],
            [],
            id="should only create the tests for the function that has been selected",
        ),
    ],
)
def test_create_test(case_name, transformers, expected_diagnostics) -> None:
    usecase_root = f"{PARENT}/cases/{case_name}"
    before_paths = list(Path(f"{usecase_root}/before").rglob("**/*.py"))
    after_paths = list(Path(f"{usecase_root}/after").rglob("**/*.py"))

    refactored_code, _diagnostics = multi_file_refactor(
        usecase_root, before_paths, transformers, RULE_MAPPING, format_code=True
    )
    assert refactored_code
    assert (
        diff_code_lfs(
            rows_to_lf(paths_to_rows(after_paths, "expected"), usecase_root),
            rows_to_lf(code_map_to_rows(refactored_code, "actual"), usecase_root),
        )
        == {}
    )
