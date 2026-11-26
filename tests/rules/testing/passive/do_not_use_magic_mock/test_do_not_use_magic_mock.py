from pathlib import Path

import pytest
from libcst.metadata import CodePosition, CodeRange

from libcst_code_mods.core.diagnostics import Diagnostic
from libcst_code_mods.engine import multi_file_refactor
from libcst_code_mods.rules._rule_mapping import RULE_MAPPING
from libcst_code_mods.rules.testing.passive.do_not_use_magic_mock import DoNotUseMagicMock

PARENT = Path(__file__).parent


@pytest.mark.parametrize(
    ("case_name", "transformers", "expected_diagnostic"),
    [
        pytest.param(
            "case_1",
            [DoNotUseMagicMock()],
            [
                Diagnostic(
                    rule="do_not_use_magic_mock",
                    path=Path("before/test_file_1.py"),
                    code_range=CodeRange(CodePosition(5, 11), CodePosition(5, 22)),
                    code="MagicMock()",
                    instead="Refactor for testability. Move I/O to the system boundary. Inject dependencies. Use small test doubles instead of MagicMock",
                )
            ],
        )
    ],
)
def test_do_not_use_magic_mock(case_name, transformers, expected_diagnostic) -> None:
    usecase_root = f"{PARENT}/cases/{case_name}"
    before_paths = list(Path(f"{usecase_root}/before").rglob("**/*.py"))
    _after_paths = list(Path(f"{usecase_root}/after").rglob("**/*.py"))

    refactored_code, diagnostics = multi_file_refactor(
        usecase_root, before_paths, transformers, RULE_MAPPING, format_code=True
    )
    assert not refactored_code
    assert diagnostics == expected_diagnostic
