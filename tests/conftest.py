from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def global_test_root() -> Path:
    return Path(__file__).parent
