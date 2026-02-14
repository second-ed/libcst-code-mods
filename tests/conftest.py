from pathlib import Path
from types import MappingProxyType

import pytest

REPO_ROOT = Path(__file__).parents[1]


@pytest.fixture(scope="session")
def fixture_get_matcher_files() -> MappingProxyType[str, str]:
    paths = Path(f"{REPO_ROOT}/tests/test_examples").rglob("**/*.py")
    return MappingProxyType({p.stem: p.read_text() for p in paths})


@pytest.fixture
def fixture_get_matcher_case(
    request: pytest.FixtureRequest, fixture_get_matcher_files: MappingProxyType[str, str]
) -> str:
    return fixture_get_matcher_files[request.param]


@pytest.fixture(scope="session")
def fixture_get_usecase_files() -> MappingProxyType[str, str]:
    paths = Path(f"{REPO_ROOT}/tests/test_transformer_cases").rglob("**/*.py")
    return {tuple(p.with_suffix("").parts[-2:]): p.read_text() for p in paths if p.stem != "__init__"}


@pytest.fixture
def fixture_get_usecase_case(
    request: pytest.FixtureRequest, fixture_get_usecase_files: MappingProxyType[str, str]
) -> str:
    return fixture_get_usecase_files[(request.param, "before")], fixture_get_usecase_files[(request.param, "after")]
