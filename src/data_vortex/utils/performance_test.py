import os
from time import time
from typing import List

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.data_vortex.database.models import Base, RentalListing

engine = create_engine("sqlite:///performance_test_db.db")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def delete_existing_db(db_path: str):
    if os.path.exists(db_path):
        os.remove(db_path)


def create_database():
    Base.metadata.create_all(bind=engine)


def synthetic_rental_listing_factory(no_listings: int) -> List[RentalListing]:
    return [
        RentalListing(
            property_id=str(i),
            image_urls=["https://example.com/image.jpg"],
            description="A lovely property",
            price_amount=1000,
            price_currency="GBP",
            added_date="2021-01-01",
            address="123 Fake Street",
            postcode="AB1 2CD",
        )
        for i in range(no_listings)
    ]


def prepare_and_run_tests():
    """Prepare the database and run performance tests"""
    delete_existing_db("performance_test_db.db")
    create_database()

    # Create a session and insert synthetic data
    with SessionLocal() as session:
        listings = synthetic_rental_listing_factory(
            1000
        )  # Adjust number for your test scale
        start_time = time()
        session.bulk_save_objects(listings)
        session.commit()
        elapsed_time = time() - start_time
        print(f"Inserted 1000 listings in {elapsed_time:.2f} seconds")
