from typing import Generator
from unittest.mock import patch

import pytest
from data_vortex.database.crud import create_listing, upsert_listing, get_listing, bulk_upsert_listings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.data_vortex.database.models import Base, RentalListing


@pytest.fixture(scope="module")
def engine():
    return create_engine("sqlite:///:memory:")


@pytest.fixture(scope="module")
def SessionLocal(engine):
    Base.metadata.create_all(bind=engine)
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture()
def db_session(SessionLocal) -> Generator[SessionLocal, None, None]:
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture()
def rental_listing(request) -> RentalListing:
    return RentalListing(
        property_id=request.param,
        description=f"Test Listing no. {request.param}",
    )


@pytest.mark.parametrize("rental_listing", ["123"], indirect=True)
def test_create_new_listing(db_session, rental_listing):
    count = db_session.query(RentalListing).count()
    result = create_listing(db_session, rental_listing)
    assert result == rental_listing
    assert result.property_id == "123"
    assert db_session.query(RentalListing).count() == count + 1


@pytest.mark.parametrize("rental_listing", ["124"], indirect=True)
def test_return_existing_listing_on_create(db_session, rental_listing):
    db_session.add(rental_listing)
    db_session.commit()
    count = db_session.query(RentalListing).count()

    result = create_listing(db_session, rental_listing)
    assert result == rental_listing
    assert db_session.query(RentalListing).count() == count


@pytest.mark.parametrize("rental_listing", ["125"], indirect=True)
def test_upsert(db_session, rental_listing):
    query_result = db_session.query(RentalListing).filter_by(property_id="125")
    assert query_result.count() == 0

    result = upsert_listing(db_session, rental_listing)
    query_result = db_session.query(RentalListing).filter_by(property_id="125")
    assert query_result.count() == 1
    assert query_result.first().description == "Test Listing no. 125"
    assert result == rental_listing

    listing_for_upsert = RentalListing(
        property_id=125, description="New description!"
    )

    result = upsert_listing(db_session, listing_for_upsert)
    query_result = db_session.query(RentalListing).filter_by(property_id="125")
    assert query_result.count() == 1
    assert query_result.first().description == "New description!"
    assert result == listing_for_upsert


@pytest.mark.parametrize("rental_listing", ["126"], indirect=True)
def test_get_existing_listing(db_session, rental_listing):
    db_session.add(rental_listing)
    db_session.commit()

    fetched_listing = get_listing(db_session, "126")
    assert fetched_listing is not None
    assert fetched_listing.property_id == "126"
    assert fetched_listing.description == "Test Listing no. 126"


def test_get_non_existent_listing(db_session):
    fetched_listing = get_listing(db_session, "999")
    assert fetched_listing is None


@pytest.fixture
def new_and_existing_listings(db_session):
    existing1 = RentalListing(property_id="200", description="Old Description 200")
    existing2 = RentalListing(property_id="201", description="Old Description 201")
    db_session.add_all([existing1, existing2])
    db_session.commit()

    new_listing = RentalListing(property_id="202", description="New Listing 202")
    update_listing = RentalListing(property_id="200", description="Updated Description 200")
    return [new_listing, update_listing]

def test_bulk_upsert_inserts_new_and_updates_existing(db_session, new_and_existing_listings):
    bulk_upsert_listings(db_session, new_and_existing_listings)

    new_insert = db_session.query(RentalListing).filter_by(property_id="202").one()
    assert new_insert.description == "New Listing 202"

    updated = db_session.query(RentalListing).filter_by(property_id="200").one()
    assert updated.description == "Updated Description 200"

    assert db_session.query(RentalListing).count() == 3


def test_bulk_upsert_rollback_on_error(db_session, new_and_existing_listings):
    with patch('sqlalchemy.orm.Session.bulk_save_objects', side_effect=Exception("Simulated Failure")):
        with pytest.raises(Exception) as exc_info:
            bulk_upsert_listings(db_session, new_and_existing_listings)

        assert "Database error during bulk upsert" in str(exc_info.value)

    assert db_session.query(RentalListing).count() == 2
