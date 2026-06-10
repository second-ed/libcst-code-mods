import string
from pathlib import Path

import hypothesis.strategies as st
from hypothesis import given

from libcst_code_mods.utils import diff_code_maps

st_paths = st.text(alphabet=string.ascii_letters + string.digits, max_size=20).map(Path)
st_path_maps = st.dictionaries(keys=st_paths, values=st.text(min_size=20), min_size=3, max_size=3)


@given(snapshot=st_path_maps)
def test_diff_code_maps_when_no_diffs(snapshot):
    assert diff_code_maps(snapshot, snapshot) == {}


@st.composite
def non_matching_code_maps(draw) -> tuple[dict, dict]:
    expected = draw(st_path_maps)
    changed_path = draw(st.sampled_from(list(expected)))
    actual = {changed_path: draw(st.text().filter(lambda s: s != expected[changed_path]))}
    return expected, actual


@given(args=non_matching_code_maps())
def test_diff_code_maps_when_diffs(args) -> None:
    expected, actual = args
    assert bool(diff_code_maps(expected, actual)) is True
