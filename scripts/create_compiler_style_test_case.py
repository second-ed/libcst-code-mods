import argparse
from pathlib import Path

from libcst_code_mods.constants import REPO_ROOT


def create_test_case(transformer_name: str, case_num: int) -> None:
    root = Path(REPO_ROOT) / f"tests/rules/{transformer_name}/cases/case_{case_num}"
    states = ["before", "after"]
    files = ["file_1", "file_2", "__init__"]

    for state in states:
        for f in files:
            new_file = root / state / f"{f}.py"
            new_file.parent.mkdir(parents=True, exist_ok=True)
            new_file.touch()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(allow_abbrev=False)
    parser.add_argument("--name", type=str, help="the name of the transformer test case to create")
    parser.add_argument("--case", type=int, help="the case number")

    args = parser.parse_args()

    create_test_case(args.name, args.case)
