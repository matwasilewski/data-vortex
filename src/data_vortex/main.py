from bs4 import BeautifulSoup

from src.data_vortex.database import crud
from src.data_vortex.database.database import SessionLocal, create_database
from src.data_vortex.database.models import RentalListing
from src.data_vortex.rightmove_models import GenericListing
from src.data_vortex.rightmove_processing import get_listings

create_database()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Example usage
def create_and_fetch_listing(listing_data: GenericListing) -> None:
    db = next(get_db())  # Get a session
    # Assuming `listing_data` is a dict with your listing data
    db_listing = RentalListing(
        property_id=listing_data.property_id,
        image_url=str(listing_data.image_url),
        description=listing_data.description,
        price_amount=listing_data.price.price,
        price_currency=listing_data.price.currency.value,
        added_date=listing_data.added_date,
        address=listing_data.address,
        postcode=listing_data.postcode,
        created_date=listing_data.created_date,
    )
    listing = crud.upsert_listing(db, rental_listing=db_listing)
    print(f"Created listing with ID: {listing.property_id}")

    fetched_listing = crud.get_listing(db, property_id=listing.property_id)
    print(f"Fetched listing: {fetched_listing.description}")


if __name__ == "__main__":
    with open(
        "/Users/mwasilewski/Code/data-vortex/tests/resources/rightmove_full_rental_query.xml"
    ) as f:
        soup = BeautifulSoup(f.read(), "html.parser")

    listings = get_listings(soup)

    for l in listings:
        create_and_fetch_listing(l)
