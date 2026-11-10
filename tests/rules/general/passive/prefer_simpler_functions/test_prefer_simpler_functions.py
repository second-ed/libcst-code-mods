from pathlib import Path

from libcst.metadata import CodePosition, CodeRange
import pytest

from libcst_code_mods.core.diagnostics import Diagnostic
from libcst_code_mods.rules._rule_mapping import RULE_MAPPING
from libcst_code_mods.rules.general.passive.prefer_simpler_functions import PreferSimplerFunctions
from libcst_code_mods.engine import multi_file_refactor
from tests.conftest import code_map_to_rows, diff_code_lfs, paths_to_rows, rows_to_lf


PARENT = Path(__file__).parent


@pytest.mark.parametrize(
    ("case_name", "transformers", "expected_diagnostics"),
    [
        pytest.param(
            "case_1",
            [PreferSimplerFunctions(branch_limit=2)],
            [
                Diagnostic(
                    "prefer_simpler_functions",
                    Path("before/file_1.py"),
                    code_range=CodeRange(CodePosition(9, 0), CodePosition(17, 12)),
                    code="\n\ndef function_with_three_decisions() -> None:\n    if condition_a:\n        pass\n\n    for item in items:\n        pass\n\n    while condition_b:\n        pass\n",
                    instead="Prefer simpler focused pure functions with no more than 2 branches. `function_with_three_decisions` has 3.",
                ),
                Diagnostic(
                    "prefer_simpler_functions",
                    Path("before/file_1.py"),
                    code_range=CodeRange(CodePosition(20, 0), CodePosition(26, 12)),
                    code="\n\ndef function_with_three_if_statements() -> None:\n    if condition_a:\n        pass\n    if condition_b:\n        pass\n    if condition_c:\n        pass\n",
                    instead="Prefer simpler focused pure functions with no more than 2 branches. `function_with_three_if_statements` has 3.",
                ),
                Diagnostic(
                    "prefer_simpler_functions",
                    Path("before/file_1.py"),
                    code_range=CodeRange(CodePosition(29, 0), CodePosition(35, 12)),
                    code="\n\ndef function_with_three_for_statements() -> None:\n    for item in items_a:\n        pass\n    for item in items_b:\n        pass\n    for item in items_c:\n        pass\n",
                    instead="Prefer simpler focused pure functions with no more than 2 branches. `function_with_three_for_statements` has 3.",
                ),
                Diagnostic(
                    "prefer_simpler_functions",
                    Path("before/file_1.py"),
                    code_range=CodeRange(CodePosition(38, 0), CodePosition(44, 12)),
                    code="\n\ndef function_with_three_while_statements() -> None:\n    while condition_a:\n        pass\n    while condition_b:\n        pass\n    while condition_c:\n        pass\n",
                    instead="Prefer simpler focused pure functions with no more than 2 branches. `function_with_three_while_statements` has 3.",
                ),
                Diagnostic(
                    "prefer_simpler_functions",
                    Path("before/file_1.py"),
                    code_range=CodeRange(CodePosition(47, 0), CodePosition(51, 31)),
                    code="\n\ndef function_with_four_if_expressions() -> None:\n    a = 1 if condition_a else 0\n    b = 1 if condition_b else 0\n    c = 1 if condition_c else 0\n    d = 1 if condition_d else 0\n",
                    instead="Prefer simpler focused pure functions with no more than 2 branches. `function_with_four_if_expressions` has 4.",
                ),
                Diagnostic(
                    "prefer_simpler_functions",
                    Path("before/file_1.py"),
                    code_range=CodeRange(CodePosition(54, 0), CodePosition(73, 12)),
                    code="\n\ndef function_with_four_except_handlers() -> None:\n    try:\n        pass\n    except ValueError:\n        pass\n\n    try:\n        pass\n    except TypeError:\n        pass\n\n    try:\n        pass\n    except RuntimeError:\n        pass\n\n    try:\n        pass\n    except Exception:\n        pass\n",
                    instead="Prefer simpler focused pure functions with no more than 2 branches. `function_with_four_except_handlers` has 4.",
                ),
                Diagnostic(
                    "prefer_simpler_functions",
                    Path("before/file_1.py"),
                    code_range=CodeRange(CodePosition(76, 0), CodePosition(88, 16)),
                    code="\n\ndef function_with_match_cases() -> None:\n    match value:\n        case 1:\n            pass\n    match value:\n        case 2:\n            pass\n    match value:\n        case 3:\n            pass\n    match value:\n        case 4:\n            pass\n",
                    instead="Prefer simpler focused pure functions with no more than 2 branches. `function_with_match_cases` has 4.",
                ),
                Diagnostic(
                    "prefer_simpler_functions",
                    Path("before/file_1.py"),
                    code_range=CodeRange(CodePosition(91, 0), CodePosition(100, 16)),
                    code="\n\ndef triggers_for_single_match_with_multiple_cases() -> None:\n    match value:\n        case 1:\n            pass\n        case 2:\n            pass\n        case 3:\n            pass\n        case 4:\n            pass\n",
                    instead="Prefer simpler focused pure functions with no more than 2 branches. `triggers_for_single_match_with_multiple_cases` has 4.",
                ),
            ],
        )
    ],
)
def test_prefer_simpler_functions(case_name, transformers, expected_diagnostics) -> None:
    usecase_root = f"{PARENT}/cases/{case_name}"
    before_paths = list(Path(f"{usecase_root}/before").rglob("**/*.py"))
    after_paths = list(Path(f"{usecase_root}/after").rglob("**/*.py"))

    refactored_code, diagnostics = multi_file_refactor(
        usecase_root, before_paths, transformers, RULE_MAPPING, format_code=True
    )
    assert not refactored_code
    assert diagnostics == expected_diagnostics
