import pickle
from pathlib import Path

import pytest
import requests
from _pytest.monkeypatch import MonkeyPatch

from data_vortex.rightmove_models import RightmoveRentParams
from data_vortex.rightmove_processing import (
    get_listings,
    process_response,
)
from data_vortex.rightmove_query import search_rental_properties


@pytest.fixture()
def mock_response(test_resources_root: Path, monkeypatch: MonkeyPatch) -> None:
    """Requests.get() mocked to return {'mock_key':'mock_response'}."""

    def mock_get(*args, **kwargs):
        return pickle.load((test_resources_root / "search_response.pkl").open("rb"))

    monkeypatch.setattr(requests, "get", mock_get)


def test_full_run(mock_response) -> None:
    respo = search_rental_properties(rightmove_params=RightmoveRentParams())
    soup = process_response(respo)
    listings = get_listings(soup)
    assert len(listings) == 25
