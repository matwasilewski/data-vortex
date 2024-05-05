import pickle
from pathlib import Path

import pytest
import requests
from _pytest.monkeypatch import MonkeyPatch

from src.data_vortex.rightmove_models import RightmoveRentParams
from src.data_vortex.rightmove_processing import (
    get_listings,
    process_response,
)
from src.data_vortex.rightmove_query import (
    get_listing_from_rightmove,
    search_rental_properties,
)


@pytest.fixture()
def _mock_response(
    test_resources_root: Path, monkeypatch: MonkeyPatch
) -> None:
    """Requests.get() mocked to return {'mock_key':'mock_response'}."""

    def mock_get(*args, **kwargs):  # noqa: ARG001
        return pickle.load(
            (test_resources_root / "search_response.pkl").open("rb")
        )

    monkeypatch.setattr(requests, "get", mock_get)


@pytest.mark.usefixtures("_mock_response")
def test_full_run() -> None:
    respo = search_rental_properties(rightmove_params=RightmoveRentParams())
    soup = process_response(respo)
    listings = get_listings(soup)
    assert len(listings) == 25


@pytest.mark.skip(reason="Actual API calls sent via this test.")
def test_unique_listings() -> None:
    initial_response = search_rental_properties(
        rightmove_params=RightmoveRentParams()
    )
    initial_soup = process_response(initial_response)
    initial_listings = get_listings(initial_soup)

    second_params = RightmoveRentParams(index=24)
    second_response = search_rental_properties(rightmove_params=second_params)
    second_soup = process_response(second_response)
    second_listings = get_listings(second_soup)

    third_params = RightmoveRentParams(index=48)
    third_response = search_rental_properties(rightmove_params=third_params)
    third_soup = process_response(third_response)
    third_listings = get_listings(third_soup)

    assert len(initial_listings) == 25
    assert len(second_listings) == 25
    assert len(third_listings) == 25

    all_listings = set(initial_listings + second_listings + third_listings)
    assert len(all_listings) == len(initial_listings) + len(
        second_listings
    ) + len(
        third_listings
    ), "There are duplicate listings across the responses."


@pytest.mark.skip(reason="Actual API calls sent via this test.")
def test_retrieve_property() -> None:
    individual_listing = get_listing_from_rightmove(
        listing_id=145826393,
    )
    assert individual_listing.status_code == 200
