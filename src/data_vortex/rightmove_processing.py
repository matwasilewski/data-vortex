import re
from typing import List

from bs4 import BeautifulSoup
from pydantic import HttpUrl, ValidationError
from requests import Response

from src.data_vortex.rightmove_models import (
    GenericListing,
    RightmoveRentalListing,
)
from src.data_vortex.utils.logging import log


def process_response(response: Response) -> BeautifulSoup:
    if response.status_code != 200:
        raise ValueError(
            f"Invalid response status code: {response.status_code} on response: {response.url}"
        )

    return BeautifulSoup(response.content, "html.parser")


def get_listings(soup: BeautifulSoup) -> List[GenericListing]:
    listings = soup.find_all("div", class_="l-searchResult")
    listings_result = []

    for listing in listings:
        property_id = listing.get("id", None).split("-")[-1]

        if property_id == "0" or property_id is None:
            log.warn("Found empty property!")
            continue

        image_urls = []
        for img in listing.find_all("img"):
            if "src" in img.attrs:
                try:
                    # Attempt to create an HttpUrl instance to validate the URL
                    validated_url = HttpUrl(img["src"])
                    image_urls.append(validated_url)
                except ValidationError:
                    # If the URL is not valid, it will not be added to the list
                    pass
        if len(image_urls) > 1:
            log.warn(f"Found multiple images for property {property_id}")
        image_url = image_urls[0] if image_urls else None

        # Extract the description
        description_elem = listing.find("span", {"itemprop": "description"})
        description = description_elem.text.strip() if description_elem else ""

        # Extract the price
        price_elem = listing.find("span", class_="propertyCard-priceValue")
        price = price_elem.text.strip() if price_elem else ""

        # Extract the added date
        added_date_elem = listing.find(
            "span", class_="propertyCard-branchSummary-addedOrReduced"
        )
        added_date = added_date_elem.text.strip() if added_date_elem else ""

        address_span = listing.find(
            "address", class_="propertyCard-address"
        ).find("span")

        address = address_span.text.strip()
        pattern = r"[A-Z]{1,2}[0-9R][0-9A-Z]?(?: [0-9][A-Z]{2})?"
        match = re.search(pattern, address)

        if match:
            postcode = match.group(0)
        else:
            postcode = None
        try:
            listing_info = GenericListing(
                property_id=property_id,
                image_url=image_url,
                description=description,
                price=price,
                added_date=added_date,
                address=address,
                postcode=postcode,
            )
            listings_result.append(listing_info)
        except ValidationError as e:
            log.error(f"Error processing listing: {e}")
            continue

    return listings_result


def get_detailed_listing(soup: BeautifulSoup) -> RightmoveRentalListing:
    # TODO: this function parser individual listing soup into a detailed listing
    # Find meta tag with property='og:url'
    url_meta_tag = soup.find("meta", property="og:url")
    property_url = url_meta_tag["content"]
    property_id_match = re.search(r"/properties/(\d+)", property_url)

    if property_id_match:
        property_id = property_id_match.group(1)
    else:
        raise ValueError("Property ID not found in the URL.")

    description_meta_tag = soup.find("meta", property="og:description")
    description = description_meta_tag.get("content", None)

    address_tag = soup.find('h1', itemprop='streetAddress')
    address = address_tag.get_text(strip=True)
    postcode = extract_postcode(address)

    return RightmoveRentalListing(
        property_id=property_id,
        description=description,
        price="5000",
        added_date="2020-10-07",
        address=address,
        postcode=postcode,
    )


def extract_postcode(address: str) -> str:
    # official UK postcode regex pattern
    postcode_pattern = (
        r"([Gg][Ii][Rr] 0[Aa]{2})|"
        r"((([A-Za-z][0-9]{1,2})|"
        r"([A-Za-z][A-Ha-hJ-Yj-y][0-9]{1,2})|"
        r"([A-Za-z][0-9][A-Za-z])|"
        r"([A-Za-z][A-Ha-hJ-Yj-y][0-9][A-Za-z]?))"
        r"\s?[0-9][A-Za-z]{2})"
    )

    match = re.search(postcode_pattern, address, re.IGNORECASE)

    if match:
        return match.group().upper()
    else:
        raise ValueError("No valid UK postcode found in the address.")
