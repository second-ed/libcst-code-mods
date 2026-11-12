import argparse
import json
import sys
from pathlib import Path

from libcst_code_mods.cache import RefactoringCache
from libcst_code_mods.config import RefactoringConfig
from libcst_code_mods.core.diagnostics import Diagnostic
from libcst_code_mods.engine import multi_file_refactor
from libcst_code_mods.rules import RULES


def cli(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", nargs="?", type=Path, default=Path.cwd())
    parser.add_argument("--config-path", type=Path)
    parser.add_argument("--fix", action="store_true")
    parser.add_argument("--black-format", action=argparse.BooleanOptionalAction, default=None)
    parser.add_argument("--rule", action="append", choices=sorted(RULES))
    args = parser.parse_args(argv)

    config = RefactoringConfig.from_file(
        args.config_path, fix=args.fix, black_format=args.black_format, rule_names=args.rule
    )
    return main(inp_root=args.path, config=config)


def main(inp_root: Path | str, config: RefactoringConfig) -> int:
    root, paths = _resolve_root_path(inp_root)
    cache = RefactoringCache.new(config, paths)

    if not cache.paths_to_process:
        return _report_no_work(config, cache)

    refactoring_rules = [RULES[k].from_dict(v) for k, v in config.rules.items() if k in RULES]
    refactored_code, diagnostics = multi_file_refactor(
        root,
        cache.paths_to_process,
        refactoring_rules=refactoring_rules,
        fix=config.fix,
        format_code=config.black_format,
    )

    _print_diagnostics(diagnostics)
    _write_refactored_code(refactored_code)
    _update_cache(cache, config, diagnostics)
    return _report_result(refactored_code, diagnostics)


def _report_no_work(config: RefactoringConfig, cache: RefactoringCache) -> int:
    if config.fix:
        cache.update()
    print("All passed")  # noqa: T201
    return 0


def _print_diagnostics(diagnostics: list[Diagnostic]) -> None:
    if diagnostics:
        print(json.dumps([diag.to_dict() for diag in diagnostics], indent=2))  # noqa: T201


def _write_refactored_code(refactored_code: dict[Path, str]) -> None:
    for path, code in refactored_code.items():
        path.write_text(code)
        print(f"Modified: {path}")  # noqa: T201


def _update_cache(cache: RefactoringCache, config: RefactoringConfig, diagnostics: list[Diagnostic]) -> None:
    if config.fix and not diagnostics:
        cache.update()


def _report_result(refactored_code: dict[Path, str], diagnostics: list[Diagnostic]) -> int:
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
