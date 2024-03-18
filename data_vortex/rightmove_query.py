from functools import lru_cache

import requests

from data_vortex.rightmove_models import RequestData, RightmoveRentParams

RIGHTMOVE_RENT_SEARCH_URL = (
    "https://www.rightmove.co.uk/property-to-rent/find.html"
)
RIGHTMOVE_HEADER = {
    "User-Agent": "curl/7.64.1",  # Example User-Agent header from curl
    # Add other headers observed from the curl command
}


def search_rental_properties(
    rightmove_params: RightmoveRentParams,
) -> requests.Response:
    request_data = RequestData(
        url=RIGHTMOVE_RENT_SEARCH_URL,
        headers=RIGHTMOVE_HEADER,
        params=rightmove_params.dict(),
    )
    return _search_rightmove(request_data)


@lru_cache
def _search_rightmove(request_data: RequestData) -> requests.Response:
    response = requests.get(
        request_data.url, params=request_data.params, headers=RIGHTMOVE_HEADER
    )
    return response
