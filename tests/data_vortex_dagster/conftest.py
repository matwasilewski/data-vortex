from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def dagster_resources_root() -> Path:
    return Path(__file__).parent / "resources"
