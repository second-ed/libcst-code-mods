import difflib
import string
from pathlib import Path

import hypothesis.strategies as st
import polars as pl
from hypothesis import given


def code_map_to_rows(code_map: dict[Path, str], code_col_name: str) -> list[dict[str, str]]:
    return [{"path": str(path), code_col_name: code} for path, code in code_map.items()]


def paths_to_rows(paths: list[Path], code_col_name: str) -> list[dict[str, str]]:
    return [{"path": str(path), code_col_name: path.read_text()} for path in paths]


def rows_to_lf(rows: list[dict[str, str]], usecase_root: str) -> pl.LazyFrame:
    return (
        pl.DataFrame(rows)
        .lazy()
        .with_columns(pl.col("path").str.replace("/after/", "/before/", literal=True).str.strip_prefix(usecase_root))
    )


def _make_diff(actual: str, expected: str) -> str:
    return "".join(
        difflib.unified_diff(
            actual.splitlines(keepends=True), expected.splitlines(keepends=True), fromfile="actual", tofile="expected"
        )
    )


def diff_code_lfs(expected: pl.LazyFrame, actual: pl.LazyFrame) -> dict[str, str]:
    non_matching = expected.join(actual, on="path").filter(pl.col("actual") != pl.col("expected"))
    diffs = (
        non_matching.with_columns(
            pl.struct(["actual", "expected"])
            .map_elements(lambda row: _make_diff(row["actual"], row["expected"]), return_dtype=pl.String)
            .alias("diff")
        )
        .select("path", "diff")
        .collect()
    )
    return dict(zip(diffs["path"], diffs["diff"], strict=True))


st_paths = st.text(alphabet=string.ascii_letters + string.digits, max_size=20).map(Path)
st_path_maps = st.dictionaries(keys=st_paths, values=st.text(), min_size=3, max_size=3)


@given(snapshot=st_path_maps)
def test_diff_code_maps_when_no_diffs(snapshot: dict[Path, str]) -> None:
    actual = rows_to_lf(code_map_to_rows(snapshot, "actual"), "")
    expected = rows_to_lf(code_map_to_rows(snapshot, "expected"), "")
    assert diff_code_lfs(expected, actual) == {}  # noqa: S101


@st.composite
def non_matching_code_maps(draw: st.DrawFn) -> tuple[dict, dict]:
    expected = draw(st_path_maps)
    changed_path = draw(st.sampled_from(list(expected)))
    actual = {changed_path: draw(st.text().filter(lambda s: s != expected[changed_path]))}
    return expected, actual


@given(args=non_matching_code_maps())
def test_diff_code_maps_when_diffs(args: tuple[dict[Path, str], dict[Path, str]]) -> None:
    expected, actual = args
    actual = rows_to_lf(code_map_to_rows(actual, "actual"), "")
    expected = rows_to_lf(code_map_to_rows(expected, "expected"), "")
    assert bool(diff_code_lfs(expected, actual)) is True  # noqa: S101
