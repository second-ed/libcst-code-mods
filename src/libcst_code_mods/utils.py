from __future__ import annotations

import difflib
from pathlib import Path

import black


def black_format(code: str, line_length: int = 120, *, magic_trailing_comma: bool = False) -> str:
    return black.format_str(
        code, mode=black.FileMode(line_length=line_length, magic_trailing_comma=magic_trailing_comma)
    )


def paths_to_code_map(paths: list[Path]) -> dict[Path, str]:
    return {p: black_format(p.read_text()) for p in paths}


def diff_code_maps(expected: dict[Path, str], actual: dict[Path, str]) -> dict[tuple[Path, Path], str]:
    diffs: dict[tuple[Path, Path], str] = {}

    actual_pairs = sorted(actual.items())
    expected_pairs = sorted(expected.items())

    for idx, expected_pair in enumerate(expected_pairs):
        expected_path, expected_code = expected_pair

        actual_path, actual_code = actual_pairs[idx]
        if actual_code == expected_code:
            continue

        diff = difflib.unified_diff(
            actual_code.splitlines(keepends=True),
            expected_code.splitlines(keepends=True),
            fromfile=f"{actual_path} (actual)",
            tofile=f"{expected_path} (expected)",
        )

        diffs[(expected_path, actual_path)] = "".join(diff)

    return diffs
