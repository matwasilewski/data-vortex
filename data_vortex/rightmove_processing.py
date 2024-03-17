from typing import List, Dict, Any

from bs4 import BeautifulSoup
from data_vortex.models import ListingInfo


def get_search_results(soup: BeautifulSoup) -> List[ListingInfo]:
    listings = soup.find_all('div', class_='l-searchResult')
    listings_result = []

    for listing in listings:
        # Initialize a dictionary to store the extracted information
        listing_info = {
            'property_id': listing.get('id', '').split('-')[-1],
            'image_urls': [img['src'] for img in listing.find_all('img') if 'src' in img.attrs],
            'description': (
                description.text.strip() if (description := listing.find('span', {'itemprop': 'description'})) else ''),
            'price': (price.text.strip() if (price := listing.find('span', class_='propertyCard-priceValue')) else ''),
            'added_date': (added_date.text.strip() if (
                added_date := listing.find('span', class_='propertyCard-branchSummary-addedOrReduced')) else ''),
            'phone_number': (phone_number.text.strip() if (
                phone_number := listing.find('a', class_='propertyCard-contactsPhoneNumber')) else '')
        }

        # Create a ListingInfo object from the dictionary
        listing_model = ListingInfo(**listing_info)

        # Append the ListingInfo object to the results list
        listings_result.append(listing_model)
