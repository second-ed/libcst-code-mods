from pathlib import Path

from libcst.metadata import CodePosition, CodeRange
import pytest

from libcst_code_mods.core.diagnostics import Diagnostic
from libcst_code_mods.rules._rule_mapping import RULE_MAPPING
from libcst_code_mods.rules.testing.passive.do_not_use_unittest import DoNotUseUnittest
from libcst_code_mods.engine import multi_file_refactor


PARENT = Path(__file__).parent


@pytest.mark.parametrize(
    ("case_name", "transformers", "expected_diagnostics"),
    [
        pytest.param(
            "case_1",
            [DoNotUseUnittest()],
            [
                Diagnostic(
                    rule="do_not_use_unittest",
                    path=Path("before/test_file_1.py"),
                    code_range=CodeRange(CodePosition(1, 0), CodePosition(1, 15)),
                    code="import unittest",
                    instead="Use pytest instead of unittest",
                ),
                Diagnostic(
                    rule="do_not_use_unittest",
                    path=Path("before/test_file_1.py"),
                    code_range=CodeRange(CodePosition(2, 0), CodePosition(2, 31)),
                    code="from unittest.mock import patch",
                    instead="Use pytest instead of unittest",
                ),
            ],
        )
    ],
)
def test_do_not_use_unittest(case_name, transformers, expected_diagnostics) -> None:
    usecase_root = f"{PARENT}/cases/{case_name}"
    before_paths = list(Path(f"{usecase_root}/before").rglob("**/*.py"))

    refactored_code, diagnostics = multi_file_refactor(
        usecase_root, before_paths, transformers, RULE_MAPPING, format_code=True
    )
    assert not refactored_code
    assert diagnostics == expected_diagnostics
