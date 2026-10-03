from pathlib import Path

from libcst.metadata import CodePosition, CodeRange
import pytest

from libcst_code_mods.core.diagnostics import AggregatedDiagnostic, Diagnostic
from libcst_code_mods.rules._rule_mapping import RULE_MAPPING
from libcst_code_mods.rules.general.passive.identify_duplicated_code import IdentifyDuplicatedCode
from libcst_code_mods.engine import multi_file_refactor

PARENT = Path(__file__).parent


@pytest.mark.parametrize(
    ("case_name", "transformers", "expected_diagnostics"),
    [
        pytest.param(
            "case_1",
            [IdentifyDuplicatedCode()],
            [
                AggregatedDiagnostic(
                    rule="identify_duplicated_code",
                    fingerprint="__name_0__ = __name_1__.clean(__name_2__)\nsave(__name_0__, limit=__literal_integer__)\n",
                    block_size=2,
                    diagnostics=(
                        Diagnostic(
                            rule="identify_duplicated_code",
                            path=Path("before/file_1.py"),
                            code_range=CodeRange(CodePosition(2, 4), end=CodePosition(3, 27)),
                            code="cleaned = obj.clean(value)\nsave(cleaned, limit=10)\n",
                            instead=None,
                        ),
                        Diagnostic(
                            rule="identify_duplicated_code",
                            path=Path("before/file_2.py"),
                            code_range=CodeRange(CodePosition(2, 4), end=CodePosition(3, 26)),
                            code="result = table.clean(item)\nsave(result, limit=50)\n",
                            instead=None,
                        ),
                    ),
                    extractable=True,
                    extraction_reason=None,
                )
            ],
        )
    ],
)
def test_identify_duplicated_code(case_name, transformers, expected_diagnostics) -> None:
    usecase_root = f"{PARENT}/cases/{case_name}"
    before_paths = list(Path(f"{usecase_root}/before").rglob("**/*.py"))
    _, diagnostics = multi_file_refactor(usecase_root, before_paths, transformers, RULE_MAPPING, fix=False)

    assert diagnostics == expected_diagnostics
