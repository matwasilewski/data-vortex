from typing import List

from bs4 import BeautifulSoup

from data_vortex.models import ListingInfo
from data_vortex.utils.logging import log


def get_listings(soup: BeautifulSoup) -> List[ListingInfo]:
    listings = soup.find_all("div", class_="l-searchResult")
    listings_result = []

    for listing in listings:
        property_id = listing.get("id", None).split("-")[-1]

        if property_id == "0" or property_id is None:
            log.warn("Found empty property!")
            continue

        # Extract the image URLs
        image_urls = [
            img["src"] for img in listing.find_all("img") if "src" in img.attrs
        ]

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

        # Extract the contact phone number
        phone_number_elem = listing.find(
            "a", class_="propertyCard-contactsPhoneNumber"
        )
        phone_number = (
            phone_number_elem.text.strip() if phone_number_elem else ""
        )

        listing_info = ListingInfo(
            property_id=property_id,
            image_urls=image_urls,
            description=description,
            price=price,
            added_date=added_date,
            phone_number=phone_number,
        )
        listings_result.append(listing_info)
    return listings_result
