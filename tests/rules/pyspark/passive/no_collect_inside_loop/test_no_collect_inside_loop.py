from pathlib import Path

from libcst.metadata import CodePosition, CodeRange
import pytest

from libcst_code_mods.core.diagnostics import Diagnostic
from libcst_code_mods.rules._rule_mapping import RULE_MAPPING
from libcst_code_mods.rules.pyspark.passive.no_collect_inside_loop import NoCollectInsideLoop
from libcst_code_mods.engine import multi_file_refactor
from tests.conftest import code_map_to_rows, diff_code_lfs, paths_to_rows, rows_to_lf


PARENT = Path(__file__).parent


@pytest.mark.parametrize(
    ("case_name", "transformers", "expected_diagnostics"),
    [
        pytest.param(
            "case_1",
            [NoCollectInsideLoop()],
            [
                Diagnostic(
                    rule="no_collect_inside_loop",
                    path=Path("before/file_1.py"),
                    code_range=CodeRange(start=CodePosition(13, 4), end=CodePosition(14, 48)),
                    code='for i in range(10):\n    df.withColumn("thing", lit(i)).collect()\n',
                    instead="build one distributed operation outside the loop",
                )
            ],
        )
    ],
)
def test_no_collect_inside_loop(case_name, transformers, expected_diagnostics) -> None:
    usecase_root = f"{PARENT}/cases/{case_name}"
    before_paths = list(Path(f"{usecase_root}/before").rglob("**/*.py"))
    after_paths = list(Path(f"{usecase_root}/after").rglob("**/*.py"))

    refactored_code, diagnostics = multi_file_refactor(
        usecase_root, before_paths, transformers, RULE_MAPPING, format_code=True
    )
    assert not refactored_code
    assert diagnostics == expected_diagnostics
