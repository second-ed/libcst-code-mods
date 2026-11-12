from pathlib import Path

from libcst.metadata import CodePosition, CodeRange
import pytest

from libcst_code_mods.core.diagnostics import Diagnostic
from libcst_code_mods.rules._rule_mapping import RULE_MAPPING
from libcst_code_mods.rules.general.passive.prefer_flatter_functions import PreferFlatterFunctions
from libcst_code_mods.engine import multi_file_refactor
from tests.conftest import code_map_to_rows, diff_code_lfs, paths_to_rows, rows_to_lf


PARENT = Path(__file__).parent


@pytest.mark.parametrize(
    ("case_name", "transformers", "expected_diagnostics"),
    [
        pytest.param(
            "case_1",
            [PreferFlatterFunctions()],
            [
                Diagnostic(
                    "prefer_flatter_functions",
                    Path("before/file_1.py"),
                    code_range=CodeRange(CodePosition(1, 0), CodePosition(6, 24)),
                    code="def function_with_four_nested_if_blocks(a: bool, b: bool, c: bool, d: bool) -> None:\n    if a:\n        if b:\n            if c:\n                if d:\n                    pass\n",
                    instead="Prefer simpler focused pure functions with no more than 3 nested indents. `function_with_four_nested_if_blocks` has 4.",
                ),
                Diagnostic(
                    "prefer_flatter_functions",
                    Path("before/file_1.py"),
                    code_range=CodeRange(CodePosition(30, 4), CodePosition(35, 28)),
                    code="def nested_function_with_four_nested_if_blocks(a: bool, b: bool, c: bool, d: bool) -> None:\n    if a:\n        if b:\n            if c:\n                if d:\n                    pass\n",
                    instead="Prefer simpler focused pure functions with no more than 3 nested indents. `nested_function_with_four_nested_if_blocks` has 4.",
                ),
            ],
        )
    ],
)
def test_prefer_flatter_functions(case_name, transformers, expected_diagnostics) -> None:
    usecase_root = f"{PARENT}/cases/{case_name}"
    before_paths = list(Path(f"{usecase_root}/before").rglob("**/*.py"))
    after_paths = list(Path(f"{usecase_root}/after").rglob("**/*.py"))

    refactored_code, diagnostics = multi_file_refactor(
        usecase_root, before_paths, transformers, RULE_MAPPING, format_code=True
    )
    assert not refactored_code
    assert diagnostics == expected_diagnostics
