import datetime

import pytest
from data_vortex.database.models import RentalListing
from data_vortex.rightmove_models import (
    Currency,
    Price,
    PriceUnit,
    RightmoveRentalListing,
)
from pydantic_core import Url


@pytest.fixture()
def rental_listing_data():
    return {
        "property_id": "123",
        "image_url": "https://media.rightmove.co.uk/dir/crop/10:9-16:9/260k/259202/144595010/259202_THECI_005196_IMG_00_0000_max_476x317.jpeg",
        "description": "Lorem ipsum",
        "price_amount": 1000,
        "price_per": "PER_MONTH",
        "price_currency": "GBP",
        "added_date": datetime.datetime(2024, 2, 10),
        "address": "123 Fake Street, N1 1AA",
        "postcode": "N1 1AA",
        "created_date": datetime.datetime(2024, 1, 10),
    }


@pytest.fixture()
def rental_listing(rental_listing_data):
    return RentalListing(**rental_listing_data)


@pytest.fixture()
def rightmove_rental_listing():
    price = Price(price=1000, currency=Currency.GBP, per=PriceUnit.PER_MONTH)
    return RightmoveRentalListing(
        property_id="123",
        image_url="https://media.rightmove.co.uk/dir/crop/10:9-16:9/260k/259202/144595010/259202_THECI_005196_IMG_00_0000_max_476x317.jpeg",
        description="Lorem ipsum",
        price=price,
        added_date="2024-02-10",
        address="123 Fake Street, N1 1AA",
        postcode="N1 1AA",
        created_date="2024-01-10",
    )


def test_load_orm_from_dict(rental_listing):
    assert rental_listing.property_id == "123"
    assert (
        rental_listing.image_url
        == "https://media.rightmove.co.uk/dir/crop/10:9-16:9/260k/259202/144595010/259202_THECI_005196_IMG_00_0000_max_476x317.jpeg"
    )
    assert rental_listing.description == "Lorem ipsum"
    assert rental_listing.price_amount == 1000
    assert rental_listing.price_per == "PER_MONTH"
    assert rental_listing.price_currency == "GBP"
    assert rental_listing.added_date == datetime.datetime(2024, 2, 10)
    assert rental_listing.address == "123 Fake Street, N1 1AA"
    assert rental_listing.postcode == "N1 1AA"
    assert rental_listing.created_date == datetime.datetime(2024, 1, 10)


def test_rightmove_to_orm_export(rightmove_rental_listing):
    orm_dict = rightmove_rental_listing.to_orm_dict()
    assert orm_dict == {
        "property_id": "123",
        "image_url": "https://media.rightmove.co.uk/dir/crop/10:9-16:9/260k/259202/144595010/259202_THECI_005196_IMG_00_0000_max_476x317.jpeg",
        "description": "Lorem ipsum",
        "price_amount": 1000,
        "price_per": "PER_MONTH",
        "price_currency": "GBP",
        "added_date": datetime.date(2024, 2, 10),
        "address": "123 Fake Street, N1 1AA",
        "postcode": "N1 1AA",
        "created_date": datetime.datetime(2024, 1, 10),
    }


def test_load_pydantic_from_orm(rental_listing) -> None:
    pyd = RightmoveRentalListing.from_orm(rental_listing)
    assert pyd.property_id == "123"
    assert pyd.image_url == Url(
        "https://media.rightmove.co.uk/dir/crop/10:9-16:9/260k/259202/144595010/259202_THECI_005196_IMG_00_0000_max_476x317.jpeg"
    )
    assert pyd.description == "Lorem ipsum"
    assert pyd.price == Price(
        price=1000, currency=Currency.GBP, per=PriceUnit.PER_MONTH
    )
    assert pyd.added_date == datetime.date(2024, 2, 10)
    assert pyd.address == "123 Fake Street, N1 1AA"
    assert pyd.postcode == "N1 1AA"
    assert pyd.created_date == datetime.datetime(2024, 1, 10)
