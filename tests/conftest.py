from pathlib import Path
from types import MappingProxyType

import pytest

REPO_ROOT = Path(__file__).parents[1]


@pytest.fixture(scope="session")
def fixture_get_files() -> MappingProxyType[str, str]:
    paths = Path(f"{REPO_ROOT}/tests/test_examples").rglob("**/*.py")
    return MappingProxyType({p.stem: p.read_text() for p in paths})


@pytest.fixture
def fixture_get_matcher_case(request: pytest.FixtureRequest, fixture_get_files: MappingProxyType[str, str]) -> str:
    for path, code in fixture_get_files.items():
        if path == request.param:
            return code
    raise ValueError(f"given invalid {request.param = }")
