from pathlib import Path

from libcst.metadata import CodePosition, CodeRange
import pytest

from libcst_code_mods.core.diagnostics import Diagnostic
from libcst_code_mods.rules._rule_mapping import RULE_MAPPING
from libcst_code_mods.rules.general.passive.do_not_use_private_functions_in_another_module import (
    DoNotUsePrivateFunctionsInAnotherModule,
)
from libcst_code_mods.engine import multi_file_refactor
from tests.conftest import code_map_to_rows, diff_code_lfs, paths_to_rows, rows_to_lf


PARENT = Path(__file__).parent


@pytest.mark.parametrize(
    ("case_name", "transformers", "expected_diagnostics"),
    [
        pytest.param(
            "case_1",
            [DoNotUsePrivateFunctionsInAnotherModule()],
            [
                Diagnostic(
                    "do_not_use_private_functions_in_another_module",
                    Path("before/file_2.py"),
                    CodeRange(CodePosition(4, 9), CodePosition(4, 29)),
                    "_private_function(1)",
                    "Use an equivalent public function. If none exists, make this function public and update its references",
                )
            ],
        ),
        pytest.param(
            "case_2",
            [DoNotUsePrivateFunctionsInAnotherModule()],
            [
                Diagnostic(
                    "do_not_use_private_functions_in_another_module",
                    Path("before/file_2.py"),
                    CodeRange(CodePosition(4, 9), CodePosition(4, 23)),
                    "public_name(1)",
                    "Use an equivalent public function. If none exists, make this function public and update its references",
                )
            ],
        ),
        pytest.param(
            "case_3",
            [DoNotUsePrivateFunctionsInAnotherModule()],
            [
                Diagnostic(
                    "do_not_use_private_functions_in_another_module",
                    Path("before/file_2.py"),
                    CodeRange(CodePosition(4, 9), CodePosition(4, 36)),
                    "module._private_function(1)",
                    "Use an equivalent public function. If none exists, make this function public and update its references",
                )
            ],
        ),
        pytest.param("case_4", [DoNotUsePrivateFunctionsInAnotherModule()], []),
    ],
)
def test_do_not_use_private_functions_in_another_module(case_name, transformers, expected_diagnostics) -> None:
    usecase_root = f"{PARENT}/cases/{case_name}"
    before_paths = list(Path(f"{usecase_root}/before").rglob("**/*.py"))
    after_paths = list(Path(f"{usecase_root}/after").rglob("**/*.py"))

    refactored_code, diagnostics = multi_file_refactor(
        usecase_root, before_paths, transformers, RULE_MAPPING, format_code=True
    )
    assert not refactored_code
    assert diagnostics == expected_diagnostics
