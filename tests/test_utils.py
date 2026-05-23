import string
from pathlib import Path

import hypothesis.strategies as st
from hypothesis import assume, given

from libcst_code_mods.utils import diff_code_maps

st_paths = st.text(alphabet=string.ascii_letters + string.digits, max_size=20).map(Path)
st_path_maps = st.dictionaries(keys=st_paths, values=st.text(min_size=20), min_size=3, max_size=3)


@given(snapshot=st_path_maps)
def test_diff_code_maps_when_no_diffs(snapshot):
    assert diff_code_maps(snapshot, snapshot) == {}


@given(expected=st_path_maps, actual=st_path_maps)
def test_diff_code_maps_when_diffs(expected, actual):
    assume(expected != actual)
    assume(sorted(expected.values()) != sorted(actual.values()))
    assert bool(diff_code_maps(expected, actual)) is True
