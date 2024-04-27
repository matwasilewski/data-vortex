from sqlite3 import DatabaseError, IntegrityError
from typing import List

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
        raise ValueError(f"Integrity error: {e!s}")
    except DatabaseError as e:
        db.rollback()
        raise Exception(f"Database error: {e!s}")


def upsert_listing(db: Session, rental_listing: RentalListing):
    try:
        db.merge(rental_listing)
        db.commit()
        return rental_listing
    except Exception as e:
        db.rollback()
        raise Exception(f"Database error during upsert: {e!s}")


def bulk_upsert_listings(
    db: Session, new_listings: List[RentalListing], unique_attr="property_id"
):
    try:
        unique_ids = [
            getattr(listing, unique_attr) for listing in new_listings
        ]

        existing_listings = (
            db.query(RentalListing)
            .filter(getattr(RentalListing, unique_attr).in_(unique_ids))
            .all()
        )
        existing_listings_dict = {
            getattr(listing, unique_attr): listing
            for listing in existing_listings
        }

        to_update = []
        to_insert = []

        for new_listing in new_listings:
            existing_listing = existing_listings_dict.get(
                getattr(new_listing, unique_attr)
            )
            if existing_listing:
                for attr, value in vars(new_listing).items():
                    setattr(existing_listing, attr, value)
                to_update.append(existing_listing)
            else:
                to_insert.append(new_listing)

        if to_update:
            db.bulk_save_objects(to_update)
        if to_insert:
            db.bulk_save_objects(to_insert)

        db.commit()
    except Exception as e:
        db.rollback()
        raise Exception(f"Database error during bulk upsert: {e}")


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
