from pathlib import Path

import pytest

from libcst_code_mods.rules._rule_mapping import RULE_MAPPING
from libcst_code_mods.rules.add_kwargs import AddKwargs
from libcst_code_mods.engine import multi_file_refactor
from libcst_code_mods.utils import diff_code_maps, paths_to_code_map

PARENT = Path(__file__).parent


@pytest.mark.parametrize(("case_name", "transformers"), [pytest.param("case_1", [AddKwargs("func")])])
def test_reorder_params(case_name, transformers) -> None:
    usecase_root = f"{PARENT}/cases/{case_name}"
    before_paths = list(Path(f"{usecase_root}/before").rglob("**/*.py"))
    after_paths = list(Path(f"{usecase_root}/after").rglob("**/*.py"))

    refactored_code = multi_file_refactor(usecase_root, before_paths, transformers, RULE_MAPPING)

    assert diff_code_maps(paths_to_code_map(after_paths), refactored_code) == {}
