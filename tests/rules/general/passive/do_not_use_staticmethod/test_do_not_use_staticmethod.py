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
    ("case_name", "transformers", "expected_diagnostics"),
    [
        pytest.param(
            "case_1",
            [DoNotUseStaticmethod()],
            [
                Diagnostic(
                    rule="do_not_use_staticmethod",
                    path=Path("before/file_1.py"),
                    code_range=CodeRange(CodePosition(3, 4), CodePosition(4, 20)),
                    code="@staticmethod\ndef should_catch_this_staticmethod(x: int, y: int) -> int:\n    return x + y\n",
                    instead="use a free floating function if the method doesn't need to be attached to the object",
                )
            ],
        )
    ],
)
def test_do_not_use_staticmethod(case_name, transformers, expected_diagnostics) -> None:
    usecase_root = f"{PARENT}/cases/{case_name}"
    before_paths = list(Path(f"{usecase_root}/before").rglob("**/*.py"))
    after_paths = list(Path(f"{usecase_root}/after").rglob("**/*.py"))

    refactored_code, diagnostics = multi_file_refactor(
        usecase_root, before_paths, transformers, RULE_MAPPING, format_code=True
    )
    assert not refactored_code
    assert diagnostics == expected_diagnostics
