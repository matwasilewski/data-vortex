from sqlalchemy.orm import Session
import json
from models import GenericListing


def create_listing(db: Session, listing_data: GenericListing):
    db_listing = GenericListing(
        property_id=listing_data.property_id,
        image_urls=json.dumps(listing_data.image_urls),
        description=listing_data.description,
        price_amount=listing_data.price_amount,
        price_currency=listing_data.price_currency,
        added_date=listing_data.added_date,
        address=listing_data.address,
        postcode=listing_data.postcode,
        created_date=listing_data.created_date
    )
    db.add(db_listing)
    db.commit()
    db.refresh(db_listing)
    return db_listing


def get_listing(db: Session, property_id: str):
    return db.query(GenericListing).filter(GenericListing.property_id == property_id).first()
