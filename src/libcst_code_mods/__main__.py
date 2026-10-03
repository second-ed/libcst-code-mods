import argparse
import json
import sys
from pathlib import Path

import yaml

from libcst_code_mods.engine import multi_file_refactor
from libcst_code_mods.rules import RULES


def main(
    inp_root: Path | str,
    specific_paths: list[str] | None = None,
    config_path: Path | str | None = None,
    *,
    fix: bool = True,
) -> int:
    root = Path(inp_root)

    if config_path is None:
        config_path = next(root.glob("refactoring-rules-config.yaml"))

    config = yaml.safe_load(Path(config_path).read_text())

    refactoring_rules = [RULES[k].from_dict(v) for k, v in config.get("rules", {}).items() if k in RULES]
    refactored_code, diagnostics = multi_file_refactor(
        root, list(root.rglob("**/*.py")), refactoring_rules=refactoring_rules, specific_paths=specific_paths, fix=fix
    )

    if diagnostics:
        print(json.dumps([diag.to_dict() for diag in diagnostics], indent=2))  # noqa: T201

    for path, code in refactored_code.items():
        path.write_text(code)
        print(f"Modified: {path}")  # noqa: T201

    return len(refactored_code)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", type=Path, default=Path.cwd())
    parser.add_argument("--specific-paths", type=lambda x: x.split(","), default=[])
    parser.add_argument("--config-path", type=str)
    parser.add_argument("--fix", action="store_true")
    args = parser.parse_args()

    sys.exit(main(inp_root=args.root, specific_paths=args.specific_paths, config_path=args.config_path, fix=args.fix))
