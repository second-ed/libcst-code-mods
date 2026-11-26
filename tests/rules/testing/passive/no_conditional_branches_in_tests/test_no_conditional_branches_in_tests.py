from pathlib import Path

import pytest
from libcst.metadata import CodePosition, CodeRange

from libcst_code_mods.core.diagnostics import Diagnostic
from libcst_code_mods.engine import multi_file_refactor
from libcst_code_mods.rules._rule_mapping import RULE_MAPPING
from libcst_code_mods.rules.testing.passive.no_conditional_branches_in_tests import NoConditionalBranchesInTests

PARENT = Path(__file__).parent


@pytest.mark.parametrize(
    ("case_name", "transformers", "expected_diagnostics"),
    [
        pytest.param(
            "case_1",
            [NoConditionalBranchesInTests()],
            [
                Diagnostic(
                    "no_conditional_branches_in_tests",
                    Path("before/test_file_1.py"),
                    CodeRange(CodePosition(6, 4), CodePosition(9, 20)),
                    "if a:\n    res = 1 == 1\nelse:\n    res = 1 == 0\n",
                    "Replace the conditional with separate test cases or parametrized inputs so each behavior is tested directly.",
                ),
                Diagnostic(
                    "no_conditional_branches_in_tests",
                    Path("before/test_file_1.py"),
                    CodeRange(CodePosition(14, 4), CodePosition(15, 18)),
                    "if a:\n    result = 1\n",
                    "Replace the conditional with separate test cases or parametrized inputs so each behavior is tested directly.",
                ),
                Diagnostic(
                    "no_conditional_branches_in_tests",
                    Path("before/test_file_1.py"),
                    CodeRange(CodePosition(19, 4), CodePosition(24, 18)),
                    "if a:\n    result = 1\nelif b:\n    result = 2\nelse:\n    result = 3\n",
                    "Replace the conditional with separate test cases or parametrized inputs so each behavior is tested directly.",
                ),
            ],
        )
    ],
)
def test_no_conditional_branches_in_tests(case_name, transformers, expected_diagnostics) -> None:
    usecase_root = f"{PARENT}/cases/{case_name}"
    before_paths = list(Path(f"{usecase_root}/before").rglob("**/*.py"))

    refactored_code, diagnostics = multi_file_refactor(
        usecase_root, before_paths, transformers, RULE_MAPPING, format_code=True
    )
    assert not refactored_code
    assert diagnostics == expected_diagnostics
