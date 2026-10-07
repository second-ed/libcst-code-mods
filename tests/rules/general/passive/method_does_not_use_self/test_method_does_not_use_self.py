from pathlib import Path

from libcst.metadata import CodePosition, CodeRange
import pytest

from libcst_code_mods.core.diagnostics import Diagnostic
from libcst_code_mods.rules._rule_mapping import RULE_MAPPING
from libcst_code_mods.rules.general.passive.method_does_not_use_self import MethodDoesNotUseSelf
from libcst_code_mods.engine import multi_file_refactor
from tests.conftest import code_map_to_rows, diff_code_lfs, paths_to_rows, rows_to_lf


PARENT = Path(__file__).parent


@pytest.mark.parametrize(
    ("case_name", "transformers", "expected_diagnostics"),
    [
        pytest.param(
            "case_1",
            [MethodDoesNotUseSelf()],
            [
                Diagnostic(
                    rule="method_does_not_use_self",
                    path=Path("before/file_1.py"),
                    code_range=CodeRange(CodePosition(5, 4), CodePosition(6, 20)),
                    code="\ndef add(self, a: int, b: int) -> int:\n    return a + b\n",
                    instead="use a free floating function if the method doesn't need to be attached to the object",
                )
            ],
        )
    ],
)
def test_method_does_not_use_self(case_name, transformers, expected_diagnostics) -> None:
    usecase_root = f"{PARENT}/cases/{case_name}"
    before_paths = list(Path(f"{usecase_root}/before").rglob("**/*.py"))
    after_paths = list(Path(f"{usecase_root}/after").rglob("**/*.py"))

    refactored_code, diagnostics = multi_file_refactor(usecase_root, before_paths, transformers, RULE_MAPPING)
    assert not refactored_code
    assert diagnostics == expected_diagnostics
