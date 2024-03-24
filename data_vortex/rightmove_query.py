import json
import time
from functools import lru_cache, wraps
from pathlib import Path

import requests
from cachetools import TTLCache

from data_vortex.rightmove_models import RequestData, RightmoveRentParams
from data_vortex.rightmove_processing import get_listings, process_response
from data_vortex.utils.config import settings
from data_vortex.utils.logging import log

RIGHTMOVE_RENT_SEARCH_URL = (
    "https://www.rightmove.co.uk/property-to-rent/find.html"
)
RIGHTMOVE_BASE_RENT_ID = "https://www.rightmove.co.uk/properties"

RIGHTMOVE_HEADER = {
    "User-Agent": "curl/7.64.1",  # Example User-Agent header from curl
}

# Define the cache with a maximum size of 100 items and items expire after 3600 seconds (1 hour)
cache = TTLCache(maxsize=1000, ttl=3600)


def cache_with_ttl(
    expiration_hours=1,
):  # Default expiration time set to 1 hour
    def decorator(fn):
        cached_fn = lru_cache(maxsize=None)(fn)

        @wraps(fn)
        def wrapper(*args, **kwargs):
            use_cache = kwargs.pop("use_cache", False)

            if (
                settings.USE_CACHE_FOR_SEARCH and use_cache
            ):  # Check if caching is enabled and requested
                now = time.time()
                ttl_seconds = (
                    expiration_hours * 3600
                )  # Convert hours to seconds

                # Create a hashable key from args and kwargs
                key = (args, tuple(sorted(kwargs.items())))

                # Check if we have a cached result and if it is still valid
                if key in cache and cache[key][1] > now:
                    return cache[key][0]

                # Call the function and cache the result along with the current time and TTL
                result = cached_fn(*args, **kwargs)
                cache[key] = (
                    result,
                    now + ttl_seconds,
                )  # Cache result with the new expiry time

                return result
            else:
                # If caching is not used or not requested, call the function directly without caching
                return fn(*args, **kwargs)

        return wrapper

    return decorator


def search_rental_properties(
    rightmove_params: RightmoveRentParams,
) -> requests.Response:
    request_data = RequestData(
        url=RIGHTMOVE_RENT_SEARCH_URL,
        headers=RIGHTMOVE_HEADER,
        params=rightmove_params.dict(),
    )
    return _search_rightmove(request_data)


@cache_with_ttl(expiration_hours=1)
def _search_rightmove(request_data: RequestData) -> requests.Response:
    response = requests.get(
        request_data.url, params=request_data.params, headers=RIGHTMOVE_HEADER
    )
    return response


def get_listing_from_rightmove(
    listing_id: int,
) -> requests.Response:
    request_data = RequestData(
        url=f"{RIGHTMOVE_BASE_RENT_ID}/{listing_id}",
        headers=RIGHTMOVE_HEADER,
    )
    return _get_listing_from_rightmove(request_data)


@cache_with_ttl(expiration_hours=24)
def _get_listing_from_rightmove(
    request_data: RequestData,
) -> requests.Response:
    response = requests.get(
        request_data.url, params=request_data.params, headers=RIGHTMOVE_HEADER
    )
    return response


def download_listing(listing_id: str) -> None:
    response = get_listing_from_rightmove(int(listing_id))
    if response.status_code != 200:
        log.error(
            f"Failed to download listing with ID {listing_id}. "
            f"Received status code: {response.status_code}"
        )
        return

    filename = Path(settings.RAW_LISTING_DIR) / f"raw_property_{listing_id}.html"
    with open(filename, "wb") as f:
        f.write(response.content)
    log.info(f"Listing with ID {listing_id} downloaded to {filename}")


def get_new_listings(
    continue_search: bool = False, download_raw_listings: bool = False, wait_time: float = 0
) -> None:
    dir_path = Path(
        settings.DATA_DIR
    )  # Ensure the path is a Path object for easier manipulation
    index = 0  # Start index

    while True:
        log.info(f"Sending new query with index: {index}")
        response = search_rental_properties(
            rightmove_params=RightmoveRentParams(index=index)
        )

        # Check for non-200 response and handle it
        if response.status_code != 200:
            log.error(f"Received non-200 response: {response.status_code}")
            break  # or handle it differently based on your requirements

        soup = process_response(response)
        listings = get_listings(soup)
        num_new_properties = 0  # Counter for new properties

        if not listings:
            log.info("No more listings retrieved, stopping...")
            break

        all_files_exist = True
        for listing in listings:
            filename = dir_path / f"property_{listing.property_id}.json"

            # Check if file already exists
            if not filename.exists():
                all_files_exist = False
                num_new_properties += 1
                listing_json = listing.model_dump_json(
                    indent=2
                )  # Assuming this method returns the JSON representation
                # Save the JSON to a file
                with open(filename, "w") as f:
                    json.dump(listing_json, f, indent=2)
                log.info(f"New listing saved: {filename}")

            if download_raw_listings:
                download_listing(listing.property_id)
                time.sleep(wait_time)

        log.info(
            f"Query outcome: {len(listings)} properties retrieved, {num_new_properties} new."
        )

        if all_files_exist and not continue_search:
            log.info("All listings already have files, stopping...")
            break

        index += 24  # Increment index for the next batch of listings
        time.sleep(wait_time)
