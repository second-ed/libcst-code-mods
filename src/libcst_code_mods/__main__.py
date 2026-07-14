from pathlib import Path

import yaml

from libcst_code_mods.engine import multi_file_refactor
from libcst_code_mods.rules import RULES


def main(inp_root: Path | str, specific_paths: list[str] | None = None, config_path: Path | str | None = None) -> None:
    root = Path(inp_root)
    paths = list(root.rglob("**/*.py"))

    if config_path is None:
        config_path = next(root.glob("refactoring-rules-config.yaml"))

    config = yaml.safe_load(Path(config_path).read_text())

    refactoring_rules = [RULES[k].from_dict(v) for k, v in config.get("rules", {}).items() if k in RULES]
    refactored_code = multi_file_refactor(
        root, paths, refactoring_rules=refactoring_rules, specific_paths=specific_paths
    )

    for path, code in refactored_code.items():
        path.write_text(code)
        print(f"Modified: {path}")  # noqa: T201
