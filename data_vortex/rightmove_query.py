import time
from functools import lru_cache, wraps

import requests
from cachetools import TTLCache

from data_vortex.rightmove_models import RequestData, RightmoveRentParams
from data_vortex.utils.config import settings

RIGHTMOVE_RENT_SEARCH_URL = (
    "https://www.rightmove.co.uk/property-to-rent/find.html"
)
RIGHTMOVE_HEADER = {
    "User-Agent": "curl/7.64.1",  # Example User-Agent header from curl
    # Add other headers observed from the curl command
}

# Define the cache with a maximum size of 100 items and items expire after 3600 seconds (1 hour)
cache = TTLCache(maxsize=1000, ttl=3600)


def cache_with_ttl(expiration_hours=1):  # Default expiration time set to 1 hour
    def decorator(fn):
        cached_fn = lru_cache(maxsize=None)(fn)

        @wraps(fn)
        def wrapper(*args, **kwargs):
            use_cache = kwargs.pop("use_cache", False)

            if settings.USE_CACHE_FOR_SEARCH and use_cache:  # Check if caching is enabled and requested
                now = time.time()
                ttl_seconds = expiration_hours * 3600  # Convert hours to seconds

                # Create a hashable key from args and kwargs
                key = (args, tuple(sorted(kwargs.items())))

                # Check if we have a cached result and if it is still valid
                if key in cache and cache[key][1] > now:
                    return cache[key][0]

                # Call the function and cache the result along with the current time and TTL
                result = cached_fn(*args, **kwargs)
                cache[key] = (result, now + ttl_seconds)  # Cache result with the new expiry time

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




@cache_with_ttl(expiration_hours=24)
def _search_rightmove(request_data: RequestData) -> requests.Response:
    response = requests.get(
        request_data.url, params=request_data.params, headers=RIGHTMOVE_HEADER
    )
    return response

