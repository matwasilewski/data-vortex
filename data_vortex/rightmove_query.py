from functools import lru_cache

import requests
from cachetools import TTLCache
from functools import lru_cache, wraps
import time

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
cache = TTLCache(maxsize=100, ttl=3600)


def cache_with_ttl(fn):
    """
    Decorator that applies both caching and a TTL policy to a function, with an optional caching feature.
    """
    cached_fn = lru_cache(maxsize=None)(fn)

    @wraps(fn)
    def wrapper(*args, **kwargs):
        use_cache = kwargs.pop('use_cache', False)

        if settings.USE_CACHE_FOR_SEARCH:
            now = time.time()

            # Create a hashable key from args and kwargs
            key = (args, tuple(sorted(kwargs.items())))

            # Check if we have a cached result and if it is still valid
            if key in cache and cache[key][1] > now:
                return cache[key][0]

            # Call the function and cache the result along with the current time
            result = cached_fn(*args, **kwargs)
            cache[key] = (result, now + 3600)  # Cache result with a new expiry time

            return result
        else:
            # If caching is not used, call the function directly without caching
            return fn(*args, **kwargs)

    return wrapper


def search_rental_properties(
        rightmove_params: RightmoveRentParams,
) -> requests.Response:
    request_data = RequestData(
        url=RIGHTMOVE_RENT_SEARCH_URL,
        headers=RIGHTMOVE_HEADER,
        params=rightmove_params.dict(),
    )
    return _search_rightmove(request_data)


@cache_with_ttl
def _search_rightmove(request_data: RequestData) -> requests.Response:
    response = requests.get(
        request_data.url, params=request_data.params, headers=RIGHTMOVE_HEADER
    )
    return response
