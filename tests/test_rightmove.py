from pathlib import Path

from data_vortex.models import RightmoveRentParams
from data_vortex.rightmove_processing import (
    process_response, get_listings,
)
from data_vortex.rightmove_query import search_rental_properties


def test_full_run() -> None:
    respo = search_rental_properties(rightmove_params=RightmoveRentParams())
    soup = process_response(respo)
    listings = get_listings(soup)
    assert len(listings) == 25
