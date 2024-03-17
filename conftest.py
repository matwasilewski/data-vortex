import os
from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def test_resources_root() -> Path:
    return Path(__file__).parent / "tests" / "resources"


