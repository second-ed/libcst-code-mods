from pathlib import Path

from libcst.metadata import CodePosition, CodeRange
import pytest

from libcst_code_mods.core.diagnostics import Diagnostic
from libcst_code_mods.rules._rule_mapping import RULE_MAPPING
from libcst_code_mods.rules.testing.passive.no_asserts_in_loop import NoAssertsInLoop
from libcst_code_mods.engine import multi_file_refactor
from tests.conftest import code_map_to_rows, diff_code_lfs, paths_to_rows, rows_to_lf


PARENT = Path(__file__).parent


@pytest.mark.parametrize(
    ("case_name", "transformers", "expected_diagnostics"),
    [
        pytest.param(
            "case_1",
            [NoAssertsInLoop()],
            [
                Diagnostic(
                    "no_asserts_in_loop",
                    Path("before/test_file_1.py"),
                    CodeRange(start=CodePosition(line=4, column=4), end=CodePosition(line=5, column=21)),
                    "\nfor i in range(n):\n    assert i >= 0\n",
                    "assert once against the entire iterable",
                )
            ],
        )
    ],
)
def test_no_asserts_in_loop(case_name, transformers, expected_diagnostics) -> None:
    usecase_root = f"{PARENT}/cases/{case_name}"
    before_paths = list(Path(f"{usecase_root}/before").rglob("**/*.py"))
    after_paths = list(Path(f"{usecase_root}/after").rglob("**/*.py"))

    refactored_code, diagnostics = multi_file_refactor(usecase_root, before_paths, transformers, RULE_MAPPING)
    assert not refactored_code
    assert diagnostics == expected_diagnostics
