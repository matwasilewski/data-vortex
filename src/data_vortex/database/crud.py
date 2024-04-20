from sqlite3 import IntegrityError

from sqlalchemy.orm import Session

from src.data_vortex.database.models import DbListing


def create_listing(db: Session, db_listing: DbListing):
    existing_listing = (
        db.query(DbListing)
        .filter(DbListing.property_id == db_listing.property_id)
        .first()
    )
    if existing_listing:
        # A listing with this property_id already exists
        # You can choose to update the existing record or just return it
        # For example, to update the existing record:
        # existing_listing.image_urls = db_listing.image_urls
        # existing_listing.description = db_listing.description
        # db.commit()
        # return existing_listing
        # Or simply return the existing record without changes:
        return existing_listing
    else:
        # No existing listing with this property_id, so add a new one
        try:
            db.add(db_listing)
            db.commit()
            db.refresh(db_listing)
            return db_listing
        except IntegrityError:
            db.rollback()
            # Handle the integrity error, e.g., by logging or raising a custom exception
            # This block catches any IntegrityError, not just uniqueness violations
            # So make sure to handle it appropriately


def get_listing(db: Session, property_id: str):
    return (
        db.query(DbListing)
        .filter(DbListing.property_id == property_id)
        .first()
    )
