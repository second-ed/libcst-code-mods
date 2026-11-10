from pathlib import Path

from libcst.metadata import CodePosition, CodeRange
import pytest

from libcst_code_mods.core.diagnostics import Diagnostic
from libcst_code_mods.rules._rule_mapping import RULE_MAPPING
from libcst_code_mods.rules.general.passive.prefer_smaller_functions import PreferSmallerFunctions
from libcst_code_mods.engine import multi_file_refactor
from tests.conftest import code_map_to_rows, diff_code_lfs, paths_to_rows, rows_to_lf


PARENT = Path(__file__).parent


@pytest.mark.parametrize(
    ("case_name", "transformers", "expected_diagnostics"),
    [
        pytest.param(
            "case_1",
            [PreferSmallerFunctions(statement_limit=2)],
            [
                Diagnostic(
                    rule="prefer_smaller_functions",
                    path=Path("before/file_1.py"),
                    code_range=CodeRange(CodePosition(10, 0), CodePosition(13, 9)),
                    code="\n\ndef function_with_three_statements() -> None:\n    x = 0\n    y = 1\n    z = 2\n",
                    instead="Prefer smaller focused pure functions with no more than 2 statements. `function_with_three_statements` has 3.",
                )
            ],
        )
    ],
)
def test_prefer_smaller_functions(case_name, transformers, expected_diagnostics) -> None:
    usecase_root = f"{PARENT}/cases/{case_name}"
    before_paths = list(Path(f"{usecase_root}/before").rglob("**/*.py"))
    after_paths = list(Path(f"{usecase_root}/after").rglob("**/*.py"))

    refactored_code, diagnostics = multi_file_refactor(
        usecase_root, before_paths, transformers, RULE_MAPPING, format_code=True
    )
    assert not refactored_code
    assert diagnostics == expected_diagnostics
