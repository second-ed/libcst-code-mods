from pathlib import Path

from libcst.metadata import CodePosition, CodeRange
import pytest

from libcst_code_mods.core.diagnostics import Diagnostic
from libcst_code_mods.rules._rule_mapping import RULE_MAPPING
from libcst_code_mods.rules.testing.passive.assert_against_full_object import AssertAgainstFullObject
from libcst_code_mods.engine import multi_file_refactor
from tests.conftest import code_map_to_rows, diff_code_lfs, paths_to_rows, rows_to_lf


PARENT = Path(__file__).parent


@pytest.mark.parametrize(
    ("case_name", "transformers", "expected_diagnostics"),
    [
        pytest.param(
            "case_1",
            [AssertAgainstFullObject()],
            [
                Diagnostic(
                    rule="assert_against_full_object",
                    path=Path("before/test_file_1.py"),
                    code_range=CodeRange(CodePosition(7, 4), CodePosition(9, 33)),
                    code="\nassert obj.a == 1\nassert obj.b == 2\nassert obj.thing == [1, 2, 3]\n",
                    instead="Assert against the entire object, not one of its attributes or subscripts.",
                ),
                Diagnostic(
                    rule="assert_against_full_object",
                    path=Path("before/test_file_1.py"),
                    code_range=CodeRange(CodePosition(15, 4), CodePosition(17, 36)),
                    code='\nassert obj["a"] == 1\nassert obj["b"] == 2\nassert obj["thing"] == [1, 2, 3]\n',
                    instead="Assert against the entire object, not one of its attributes or subscripts.",
                ),
            ],
        )
    ],
)
def test_assert_against_full_object(case_name, transformers, expected_diagnostics) -> None:
    usecase_root = f"{PARENT}/cases/{case_name}"
    before_paths = list(Path(f"{usecase_root}/before").rglob("**/*.py"))
    after_paths = list(Path(f"{usecase_root}/after").rglob("**/*.py"))

    refactored_code, diagnostics = multi_file_refactor(usecase_root, before_paths, transformers, RULE_MAPPING)
    assert not refactored_code
    assert diagnostics == expected_diagnostics
