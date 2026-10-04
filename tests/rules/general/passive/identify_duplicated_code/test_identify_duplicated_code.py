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
            [IdentifyDuplicatedCode(min_occurrences=2)],
            [
                AggregatedDiagnostic(
                    rule="identify_duplicated_code",
                    fingerprint="__name_0__ = __name_1__.clean(__name_2__)\nsave(__name_0__, limit=__literal_integer__)\n",
                    block_size=2,
                    diagnostics=(
                        Diagnostic(
                            rule="identify_duplicated_code",
                            path=Path("before/file_1.py"),
                            code_range=CodeRange(CodePosition(2, 4), CodePosition(3, 27)),
                            code="cleaned = obj.clean(value)\nsave(cleaned, limit=10)\n",
                            instead=None,
                        ),
                        Diagnostic(
                            rule="identify_duplicated_code",
                            path=Path("before/file_2.py"),
                            code_range=CodeRange(CodePosition(2, 4), CodePosition(3, 26)),
                            code="result = table.clean(item)\nsave(result, limit=50)\n",
                            instead=None,
                        ),
                    ),
                    extractable=True,
                    extraction_reason=None,
                ),
                AggregatedDiagnostic(
                    rule="identify_duplicated_code",
                    fingerprint="__name_0__, __name_1__ = fn_a(__name_2__)\nreturn __name_2__.update(body=__name_2__.body.update(body=[*__name_0__, __name_4__, *__name_2__.body.body[__name_1__:]]))\n",
                    block_size=2,
                    diagnostics=(
                        Diagnostic(
                            rule="identify_duplicated_code",
                            path=Path("before/file_1.py"),
                            code_range=CodeRange(CodePosition(7, 4), CodePosition(8, 105)),
                            code="res_a, res_b = fn_a(some_arg)\nreturn some_arg.update(body=some_arg.body.update(body=[*res_a, guards, *some_arg.body.body[res_b:]]))\n",
                            instead=None,
                        ),
                        Diagnostic(
                            rule="identify_duplicated_code",
                            path=Path("before/file_2.py"),
                            code_range=CodeRange(CodePosition(7, 4), CodePosition(8, 105)),
                            code="res_a, res_b = fn_a(some_arg)\nreturn some_arg.update(body=some_arg.body.update(body=[*res_a, debugs, *some_arg.body.body[res_b:]]))\n",
                            instead=None,
                        ),
                    ),
                    extractable=True,
                    extraction_reason=None,
                ),
            ],
        )
    ],
)
def test_identify_duplicated_code(case_name, transformers, expected_diagnostics) -> None:
    usecase_root = f"{PARENT}/cases/{case_name}"
    before_paths = list(Path(f"{usecase_root}/before").rglob("**/*.py"))
    _, diagnostics = multi_file_refactor(usecase_root, before_paths, transformers, RULE_MAPPING, fix=False)

    assert _diags_to_dicts(diagnostics) == _diags_to_dicts(expected_diagnostics)


def _diags_to_dicts(diagnostics: list[Diagnostic]) -> list[dict]:
    return [d.to_dict() for d in diagnostics]
