from sqlite3 import DatabaseError, IntegrityError

from sqlalchemy.orm import Session

from src.data_vortex.database.models import RentalListing


def create_listing(db: Session, rental_listing: RentalListing):
    try:
        existing_listing = (
            db.query(RentalListing)
            .filter(RentalListing.property_id == rental_listing.property_id)
            .first()
        )
        if existing_listing:
            return existing_listing
        else:
            db.add(rental_listing)
            db.commit()
            db.refresh(rental_listing)
            return rental_listing
    except IntegrityError as e:
        db.rollback()
        # Handle specific integrity issues, such as unique constraint violations
        raise ValueError(f"Integrity error: {e!s}")
    except DatabaseError as e:
        db.rollback()
        # Handle general database errors
        raise Exception(f"Database error: {e!s}")


def get_listing(db: Session, property_id: str):
    return (
        db.query(RentalListing)
        .filter(RentalListing.property_id == property_id)
        .first()
    )


def update_listing(db: Session, property_id: str, **updates):
    try:
        listing = get_listing(db, property_id)
        if listing:
            for key, value in updates.items():
                setattr(listing, key, value)
            db.commit()
            return listing
        else:
            raise ValueError("Listing not found for the provided property_id.")
    except DatabaseError as e:
        db.rollback()
        raise Exception(f"Database error during update: {e!s}")


def delete_listing(db: Session, property_id: str):
    try:
        listing = get_listing(db, property_id)
        if listing:
            db.delete(listing)
            db.commit()
        else:
            raise ValueError("Listing not found for the provided property_id.")
    except DatabaseError as e:
        db.rollback()
        raise Exception(f"Database error during deletion: {e!s}")
