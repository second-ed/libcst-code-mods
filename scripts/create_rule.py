import argparse
from pathlib import Path

from libcst_code_mods.constants import REPO_ROOT

SRC_FILE = """import attrs

from libcst_code_mods.core.base_cst_transformer import BaseCstTransformer
from libcst_code_mods.core.base_cst_visitor import BaseCstVisitor
from libcst_code_mods.core.refactoring_rule import RefactoringRule
from libcst_code_mods.rules._rule_mapping import register_rule, register_rule_transformer, register_rule_visitor


@register_rule
@attrs.define(frozen=True)
class {cls_name}(RefactoringRule):
    pass


@register_rule_visitor({cls_name})
@attrs.define
class {cls_name}Visitor(BaseCstVisitor):
    pass


@register_rule_transformer({cls_name})
@attrs.define
class {cls_name}Transformer(BaseCstTransformer):
    pass
"""


TEST_FILE = """from pathlib import Path

import pytest

from libcst_code_mods.rules._rule_mapping import RULE_MAPPING
from libcst_code_mods.rules.{rule_path} import {cls_name}
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
    parts = transformer_name.split(".")
    module_name = parts[-1]
    file_path = "/".join(parts)

    root = Path(REPO_ROOT) / f"tests/rules/{file_path}/cases/case_{case_num}"
    states = ["before", "after"]
    files = ["file_1", "__init__"]

    for state in states:
        for f in files:
            new_file = root / state / f"{f}.py"
            new_file.parent.mkdir(parents=True, exist_ok=True)
            new_file.touch()

    cls_name = "".join(map(str.capitalize, module_name.split("_")))
    (Path(REPO_ROOT) / f"tests/rules/{file_path}/test_{module_name}.py").write_text(
        TEST_FILE.format(rule_name=module_name, rule_path=transformer_name, cls_name=cls_name)
    )


def create_src_file(transformer_name: str) -> None:
    parts = transformer_name.split(".")
    module_name = parts[-1]
    file_path = "/".join(parts)

    cls_name = "".join(map(str.capitalize, module_name.split("_")))

    path = Path(REPO_ROOT) / f"src/libcst_code_mods/rules/{file_path}.py"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(SRC_FILE.format(cls_name=cls_name))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(allow_abbrev=False)
    parser.add_argument("--name", type=str, help="the name of the transformer test case to create")
    parser.add_argument("--case", type=int, help="the case number")

    args = parser.parse_args()
    create_src_file(args.name)
    create_test_case(args.name, args.case)
