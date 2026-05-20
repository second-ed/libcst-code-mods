import argparse
from pathlib import Path

from libcst_code_mods.constants import REPO_ROOT


def create_test_case(transformer_name: str, case_num: int) -> None:
    root = Path(REPO_ROOT) / f"tests/test_transformer_cases/{transformer_name}/case_{case_num}"
    root.mkdir(parents=True, exist_ok=True)
    for file in ["before", "after"]:
        (root / f"{file}.py").touch()

    (REPO_ROOT / f"tests/transformers/test_{transformer_name}.py").touch()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(allow_abbrev=False)
    parser.add_argument("--name", type=str, help="the name of the transformer test case to create")
    parser.add_argument("--case", type=int, help="the case number")

    args = parser.parse_args()

    create_test_case(args.name, args.case)
