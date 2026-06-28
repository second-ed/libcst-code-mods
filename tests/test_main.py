from shutil import copytree

from libcst_code_mods.__main__ import main
from libcst_code_mods.constants import REPO_ROOT
from tests.conftest import diff_code_lfs, paths_to_rows, rows_to_lf


def test_main(tmp_path) -> None:
    root = REPO_ROOT / "mock_package"
    config_path = REPO_ROOT / "tests/test-refactoring-rules-config.yaml"

    tmp_root = tmp_path / "mock_package"
    copytree(root, tmp_root)
    before_root = tmp_root / "before"
    after_root = tmp_root / "after"

    main(before_root, config_path=config_path)

    expected_paths = list(after_root.rglob("**/*.py"))
    actual_paths = list(before_root.rglob("**/*.py"))

    assert (
        diff_code_lfs(
            rows_to_lf(paths_to_rows(expected_paths, "expected"), str(tmp_root)),
            rows_to_lf(paths_to_rows(actual_paths, "actual"), str(tmp_root)),
        )
        == {}
    )
