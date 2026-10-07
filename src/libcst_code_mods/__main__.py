import argparse
import json
import sys
from pathlib import Path

import yaml

from libcst_code_mods.engine import multi_file_refactor
from libcst_code_mods.rules import RULES


def cli() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", nargs="?", type=Path, default=Path.cwd())
    parser.add_argument("--config-path", type=str)
    parser.add_argument("--fix", action="store_true")
    args = parser.parse_args()

    return main(inp_root=args.path, config_path=args.config_path, fix=args.fix)


def main(inp_root: Path | str, config_path: Path | str | None = None, *, fix: bool = True) -> int:
    root, paths = _resolve_root_path(inp_root)

    if config_path is None:
        config_path = next(Path.cwd().glob("refactoring-rules-config.yaml"))

    config = yaml.safe_load(Path(config_path).read_text())

    refactoring_rules = [RULES[k].from_dict(v) for k, v in config.get("rules", {}).items() if k in RULES]
    refactored_code, diagnostics = multi_file_refactor(root, paths, refactoring_rules=refactoring_rules, fix=fix)

    if diagnostics:
        print(json.dumps([diag.to_dict() for diag in diagnostics], indent=2))  # noqa: T201

    for path, code in refactored_code.items():
        path.write_text(code)
        print(f"Modified: {path}")  # noqa: T201

    n_changes = len(refactored_code)
    n_diagnostics = len(diagnostics)

    if (n_changes + n_diagnostics) == 0:
        print("All passed")  # noqa: T201
        return 0

    print(f"`{n_changes}` changes made. `{n_diagnostics}` required")  # noqa: T201
    return n_changes + n_diagnostics


def _resolve_root_path(inp_root: Path | str) -> tuple[Path, list[Path]]:
    target = Path(inp_root).resolve()

    if target.is_file():
        root, paths = target.parent, [target]
    elif target.is_dir():
        root = target
        paths = list(root.rglob("*.py"))
    else:
        raise FileNotFoundError(f"Target does not exist: {target}")
    return root, paths


if __name__ == "__main__":
    sys.exit(cli())
