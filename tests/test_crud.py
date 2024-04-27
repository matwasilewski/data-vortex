from typing import Generator

import pytest
from data_vortex.database.crud import create_listing, upsert_listing
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
