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
    root = Path(inp_root).resolve()

    if config_path is None:
        config_path = next(Path.cwd().glob("refactoring-rules-config.yaml"))

    config = yaml.safe_load(Path(config_path).read_text())
    paths = _filter_paths(list(root.rglob("**/*.py")), specific_paths or [])

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


def _filter_paths(paths: list[Path], specific_paths: list[str]) -> list[Path]:
    if specific_paths:
        paths = [p for p in paths if str(p) in specific_paths]
    return paths


def cli() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", type=Path, default=Path.cwd())
    parser.add_argument("--specific-paths", type=lambda x: x.split(","), default=[])
    parser.add_argument("--config-path", type=str)
    parser.add_argument("--fix", action="store_true")
    args = parser.parse_args()

    return main(inp_root=args.root, specific_paths=args.specific_paths, config_path=args.config_path, fix=args.fix)


if __name__ == "__main__":
    sys.exit(cli())
