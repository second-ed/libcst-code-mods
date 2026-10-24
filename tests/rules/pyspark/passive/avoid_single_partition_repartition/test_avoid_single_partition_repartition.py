from pathlib import Path

from libcst.metadata import CodePosition, CodeRange
import pytest

from libcst_code_mods.core.diagnostics import Diagnostic
from libcst_code_mods.rules._rule_mapping import RULE_MAPPING
from libcst_code_mods.rules.pyspark.passive.avoid_single_partition_repartition import AvoidSinglePartitionRepartition
from libcst_code_mods.engine import multi_file_refactor
from tests.conftest import code_map_to_rows, diff_code_lfs, paths_to_rows, rows_to_lf


PARENT = Path(__file__).parent


@pytest.mark.parametrize(
    ("case_name", "transformers", "expected_diagnostics"),
    [
        pytest.param(
            "case_1",
            [AvoidSinglePartitionRepartition()],
            [
                Diagnostic(
                    "avoid_single_partition_repartition",
                    Path("before/file_1.py"),
                    CodeRange(CodePosition(10, 4), CodePosition(10, 45)),
                    'df.repartition(1).write.parquet("./blah")',
                    "This call forces 1 output partition. Remove it or use a partition count that matches the workload.",
                ),
                Diagnostic(
                    "avoid_single_partition_repartition",
                    Path("before/file_1.py"),
                    CodeRange(CodePosition(14, 4), CodePosition(14, 42)),
                    'df.coalesce(1).write.parquet("./blah")',
                    "This call forces 1 output partition. Remove it or use a partition count that matches the workload.",
                ),
            ],
        )
    ],
)
def test_avoid_single_partition_repartition(case_name, transformers, expected_diagnostics) -> None:
    usecase_root = f"{PARENT}/cases/{case_name}"
    before_paths = list(Path(f"{usecase_root}/before").rglob("**/*.py"))
    after_paths = list(Path(f"{usecase_root}/after").rglob("**/*.py"))

    refactored_code, diagnostics = multi_file_refactor(
        usecase_root, before_paths, transformers, RULE_MAPPING, format_code=True
    )
    assert not refactored_code
    assert diagnostics == expected_diagnostics
