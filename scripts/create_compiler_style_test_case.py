import argparse
from pathlib import Path

from libcst_code_mods.constants import REPO_ROOT

TEST_FILE = """from pathlib import Path

import pytest

from libcst_code_mods.rules._rule_mapping import RULE_MAPPING
from libcst_code_mods.rules.{rule_name} import {cls_name}
from libcst_code_mods.engine import multi_file_refactor
from tests.conftest import code_map_to_rows, diff_code_lfs, paths_to_rows, rows_to_lf


PARENT = Path(__file__).parent


@pytest.mark.parametrize(("case_name", "transformers"), [pytest.param("case_1", [{cls_name}()])])
def test_{rule_name}(case_name, transformers) -> None:
    usecase_root = f"{{PARENT}}/cases/{{case_name}}"
    before_paths = list(Path(f"{{usecase_root}}/before").rglob("**/*.py"))
    after_paths = list(Path(f"{{usecase_root}}/after").rglob("**/*.py"))

    refactored_code = multi_file_refactor(usecase_root, before_paths, transformers, RULE_MAPPING)
    assert refactored_code
    assert (
        diff_code_lfs(
            rows_to_lf(paths_to_rows(after_paths, "expected"), usecase_root),
            rows_to_lf(code_map_to_rows(refactored_code, "actual"), usecase_root),
        )
        == {{}}
    )
"""


def create_test_case(transformer_name: str, case_num: int) -> None:
    root = Path(REPO_ROOT) / f"tests/rules/{transformer_name}/cases/case_{case_num}"
    states = ["before", "after"]
    files = ["file_1", "file_2", "__init__"]

    for state in states:
        for f in files:
            new_file = root / state / f"{f}.py"
            new_file.parent.mkdir(parents=True, exist_ok=True)
            new_file.touch()

    cls_name = "".join(map(str.capitalize, transformer_name.split("_")))
    (Path(REPO_ROOT) / f"tests/rules/{transformer_name}/test_{transformer_name}.py").write_text(
        TEST_FILE.format(rule_name=transformer_name, cls_name=cls_name)
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(allow_abbrev=False)
    parser.add_argument("--name", type=str, help="the name of the transformer test case to create")
    parser.add_argument("--case", type=int, help="the case number")

    args = parser.parse_args()

    create_test_case(args.name, args.case)
