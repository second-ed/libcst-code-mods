from pathlib import Path

from libcst.metadata import CodePosition, CodeRange
import pytest

from libcst_code_mods.core.diagnostics import Diagnostic
from libcst_code_mods.rules._rule_mapping import RULE_MAPPING
from libcst_code_mods.rules.testing.passive.do_not_use_test_classes import DoNotUseTestClasses
from libcst_code_mods.engine import multi_file_refactor


PARENT = Path(__file__).parent


@pytest.mark.parametrize(
    ("case_name", "transformers", "expected_diagnostics"),
    [
        pytest.param(
            "case_1",
            [DoNotUseTestClasses()],
            [
                Diagnostic(
                    rule="do_not_use_test_classes",
                    path=Path("before/test_file_1.py"),
                    code_range=CodeRange(CodePosition(1, 0), CodePosition(3, 20)),
                    code="class TestNumbers:\n    def test_positive(self) -> None:\n        assert 1 > 0\n",
                    instead="use a parametrized pytest function instead",
                )
            ],
        )
    ],
)
def test_do_not_use_test_classes(case_name, transformers, expected_diagnostics) -> None:
    usecase_root = f"{PARENT}/cases/{case_name}"
    before_paths = list(Path(f"{usecase_root}/before").rglob("**/*.py"))

    refactored_code, diagnostics = multi_file_refactor(usecase_root, before_paths, transformers, RULE_MAPPING)
    assert not refactored_code
    assert diagnostics == expected_diagnostics
