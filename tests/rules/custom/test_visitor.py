from pathlib import Path

from libcst.metadata import CodePosition, CodeRange
import pytest

from libcst_code_mods.core.diagnostics import Diagnostic
from libcst_code_mods.rules._rule_mapping import RULE_MAPPING
from libcst_code_mods.rules.general.passive.do_not_use_staticmethod import DoNotUseStaticmethod
from libcst_code_mods.engine import multi_file_refactor
from tests.conftest import code_map_to_rows, diff_code_lfs, paths_to_rows, rows_to_lf


PARENT = Path(__file__).parent


@pytest.mark.parametrize(
    ("case_name", "custom_rules", "expected_diagnostics"),
    [
        pytest.param(
            "case_1",
            {
                "no_print": {
                    "matcher": {"type": "Call", "func": {"type": "Name", "value": "print"}},
                    "instead": "use the project logger",
                }
            },
            [
                Diagnostic(
                    rule="no_print",
                    path=Path("before/file_1.py"),
                    code_range=CodeRange(CodePosition(1, 0), CodePosition(1, 13)),
                    code='print("blah")',
                    instead="use the project logger",
                )
            ],
        )
    ],
)
def test_custom_diagnostic_visitor(case_name, custom_rules, expected_diagnostics) -> None:
    usecase_root = f"{PARENT}/cases/{case_name}"
    before_paths = list(Path(f"{usecase_root}/before").rglob("**/*.py"))
    after_paths = list(Path(f"{usecase_root}/after").rglob("**/*.py"))

    refactored_code, diagnostics = multi_file_refactor(
        usecase_root, before_paths, [], RULE_MAPPING, custom_rules=custom_rules, format_code=True
    )
    assert not refactored_code
    assert diagnostics == expected_diagnostics
