import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from data_vortex.database.crud import create_listing
from src.data_vortex.database.models import Base, RentalListing


@pytest.fixture(scope="module")
def engine():
    return create_engine('sqlite:///:memory:')


@pytest.fixture(scope="module")
def SessionLocal(engine):
    Base.metadata.create_all(bind=engine)
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def db_session(SessionLocal):
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture
def rental_listing(request) -> RentalListing:
    return RentalListing(property_id=request.param, description="Test Listing")


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
