from typing import Generator, List

import pytest
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker

from src.data_vortex.database.crud import (
    bulk_upsert_listings,
    get_listing,
    upsert_listing,
)
from src.data_vortex.database.models import Base, RentalListing
from src.data_vortex.rightmove_models import (
    Currency,
    Price,
    PriceUnit,
    RightmoveRentalListing,
)
from src.data_vortex.utils.conversion import orm2pydantic_rental_listing


@pytest.fixture(scope="module")
def engine() -> Engine:
    return create_engine("sqlite:///:memory:")


@pytest.fixture(scope="module")
def SessionLocal(engine: Engine) -> sessionmaker:
    Base.metadata.create_all(bind=engine)
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture()
def db_session(
    SessionLocal: sessionmaker,
) -> Generator[SessionLocal, None, None]:
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture()
def rental_listing(request) -> RightmoveRentalListing:
    return RightmoveRentalListing(
        property_id=request.param,
        description=f"Test Listing no. {request.param}",
        price=Price(
            price=1000, currency=Currency.GBP, per=PriceUnit.PER_MONTH
        ),
        added_date="2021-01-01",
        address="123 Fake Street, AB12 3CD",
        postcode="AB12 3CD",
    )


@pytest.mark.parametrize("rental_listing", ["123"], indirect=True)
def test_create_new_listing(
    db_session: SessionLocal, rental_listing: RightmoveRentalListing
) -> None:
    count = db_session.query(RentalListing).count()
    upsert_listing(db_session, rental_listing)
    result = db_session.query(RentalListing).filter_by(property_id="123").one()
    pydantic_result = orm2pydantic_rental_listing(result)

    assert rental_listing is not None
    assert pydantic_result is not None
    assert rental_listing.property_id == pydantic_result.property_id
    assert rental_listing.description == pydantic_result.description
    assert rental_listing.price == pydantic_result.price
    assert rental_listing.added_date == pydantic_result.added_date
    assert rental_listing.address == pydantic_result.address
    assert rental_listing.postcode == pydantic_result.postcode
    assert rental_listing.created_date == pydantic_result.created_date
    assert rental_listing.price.dict() == pydantic_result.price.dict()

    assert pydantic_result.dict() == rental_listing.dict()
    assert pydantic_result == rental_listing
    assert pydantic_result.property_id == "123"
    assert db_session.query(RentalListing).count() == count + 1


@pytest.mark.parametrize("rental_listing", ["124"], indirect=True)
def test_no_error_on_double_create(
    db_session: SessionLocal, rental_listing: RightmoveRentalListing
):
    # Create the listing
    upsert_listing(db_session, rental_listing)
    count = db_session.query(RentalListing).count()

    # Attempt to create the same listing again
    upsert_listing(db_session, rental_listing)
    assert db_session.query(RentalListing).count() == count


# @pytest.mark.parametrize("rental_listing", ["125"], indirect=True)
# def test_update(db_session: SessionLocal, rental_listing: RightmoveRentalListing) -> None:
#     query_result = db_session.query(RentalListing).filter_by(property_id="125")
#     assert query_result.count() == 0
#
#     result = update_listing(db_session, rental_listing)
#     query_result = db_session.query(RentalListing).filter_by(property_id="125")
#     assert query_result.count() == 1
#     assert query_result.first().description == "Test Listing no. 125"
#     assert result == rental_listing

# listing_for_upsert = RightmoveRentalListing(
#     property_id=125, description="New description!"
# )
#
# result = upsert_listing(db_session, listing_for_upsert)
# query_result = db_session.query(RentalListing).filter_by(property_id="125")
# assert query_result.count() == 1
# assert query_result.first().description == "New description!"
# assert result == listing_for_upsert


@pytest.mark.parametrize("rental_listing", ["126"], indirect=True)
def test_get_existing_listing(
    db_session: SessionLocal, rental_listing: RightmoveRentalListing
) -> None:
    upsert_listing(db_session, rental_listing)

    fetched_listing = get_listing(db_session, "126")
    assert fetched_listing is not None
    assert fetched_listing.property_id == "126"
    assert fetched_listing.description == "Test Listing no. 126"


def test_get_non_existent_listing(db_session: SessionLocal) -> None:
    fetched_listing = get_listing(db_session, "999")
    assert fetched_listing is None


@pytest.fixture()
def new_and_existing_listings(
    db_session: SessionLocal,
) -> List[RightmoveRentalListing]:
    existing_1 = RightmoveRentalListing(
        property_id="200",
        description="Old Description 200",
        price=Price(
            price=1000, currency=Currency.GBP, per=PriceUnit.PER_MONTH
        ),
        added_date="2021-01-01",
        address="123 Fake Street, AB12 3CD",
        postcode="AB12 3CD",
    )
    existing_2 = RightmoveRentalListing(
        property_id="201",
        description="Old Description 201",
        price=Price(
            price=1000, currency=Currency.GBP, per=PriceUnit.PER_MONTH
        ),
        added_date="2021-01-01",
        address="123 Fake Street, AB12 3CD",
        postcode="AB12 3CD",
    )
    upsert_listing(db_session, existing_1)
    upsert_listing(db_session, existing_2)

    new_listing = RightmoveRentalListing(
        property_id="202",
        description="New Listing 202",
        price=Price(
            price=1000, currency=Currency.GBP, per=PriceUnit.PER_MONTH
        ),
        added_date="2021-01-01",
        address="563 Fake Street, AB12 3CD",
        postcode="AB12 3CD",
    )
    update_listing = RightmoveRentalListing(
        property_id="200",
        description="Updated Description 200",
        price=Price(
            price=1000, currency=Currency.GBP, per=PriceUnit.PER_MONTH
        ),
        added_date="2021-01-01",
        address="123 Fake Street, AB12 3CD",
        postcode="AB12 3CD",
    )

    return [new_listing, update_listing]


@pytest.mark.skip()
def test_bulk_upsert_inserts_new_and_updates_existing(
    db_session: SessionLocal,
    new_and_existing_listings: List[RightmoveRentalListing],
) -> None:
    count = db_session.query(RentalListing).count()
    bulk_upsert_listings(db_session, new_and_existing_listings)

    new_insert = (
        db_session.query(RentalListing).filter_by(property_id="202").one()
    )
    assert new_insert.description == "New Listing 202"

    updated = (
        db_session.query(RentalListing).filter_by(property_id="200").one()
    )
    assert updated.description == "Updated Description 200"

    assert db_session.query(RentalListing).count() == count + 1