from sqlite3 import DatabaseError, IntegrityError
from typing import List

from sqlalchemy import update
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.orm import Session

from src.data_vortex.database.models import RentalListing
from src.data_vortex.rightmove_models import RightmoveRentalListing
from src.data_vortex.utils.config import settings


def upsert_listing(
    db: Session, rental_listing: RightmoveRentalListing
) -> None:
    if db.get_bind().dialect.name != "sqlite":
        raise NotImplementedError(
            "Only SQLite database is supported at the moment."
        )

    try:
        listing_dict = rental_listing.to_orm_dict()
        stmt = sqlite_insert(RentalListing).values(listing_dict)
        stmt = stmt.on_conflict_do_update(
            index_elements=[RentalListing.property_id],
            set_=listing_dict,
        )
        db.execute(stmt)
    except IntegrityError as e:
        db.rollback()
        raise ValueError(f"Integrity error: {e!s}")
    except DatabaseError as e:
        db.rollback()
        raise Exception(f"Database error: {e!s}")


def bulk_upsert_listings(
    db: Session, new_listings: List[RightmoveRentalListing]
):
    raise NotImplementedError(
        "This function is not implemented yet. Please implement it."
    )
    if db.get_bind().dialect.name != "sqlite":
        raise NotImplementedError(
            "Only SQLite database is supported at the moment."
        )

    try:
        unique_ids = [listing.property_id for listing in new_listings]

        existing_listings = db.query(RentalListing).filter(
            RentalListing.property_id.in_(unique_ids)
        )

        existing_listings_dict = {
            listing.property_id: listing for listing in existing_listings
        }

        to_update = []
        to_insert = []

        for new_listing in new_listings:
            existing_listing = existing_listings_dict.get(
                new_listing.property_id
            )
            if existing_listing:
                for attr, value in vars(new_listing).items():
                    setattr(existing_listing, attr, value)
                to_update.append(existing_listing)
            else:
                to_insert.append(new_listing.to_orm_dict())

        if to_update:
            stmt = update(RentalListing).values(to_update)
            db.execute(stmt)
            db.commit()
        if to_insert:
            stmt = sqlite_insert(RentalListing).values(to_insert)
            db.execute(stmt)
            db.commit()
    except Exception as e:
        db.rollback()
        raise Exception(f"Database error during bulk upsert: {e}")


def get_listing(db: Session, property_id: str):
    if db.get_bind().dialect.name != "sqlite":
        raise NotImplementedError(
            "Only SQLite database is supported at the moment."
        )

    return (
        db.query(RentalListing)
        .filter(RentalListing.property_id == property_id)
        .first()
    )


def delete_listing(db: Session, property_id: str):
    if db.get_bind().dialect.name != "sqlite":
        raise NotImplementedError(
            "Only SQLite database is supported at the moment."
        )

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
