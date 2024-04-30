import datetime

import pytest

from data_vortex.database.models import RentalListing
from src.data_vortex.rightmove_models import (
    Currency,
    GenericListing,
    Price,
    PriceUnit,
    RightmoveRentalListing,
)


@pytest.mark.parametrize(
    "added_date",
    [
        "2024-02-10",
        "10-02-2024",
        "10/02/2024",
        "2024/02/10",
        "Added on 10/02/2024",
        "Added on 10-02-2024",
        datetime.date(2024, 2, 10),
        datetime.datetime(2024, 2, 10, 0, 0, 0),
    ],
)
def test_date_parsing(added_date: str) -> None:
    l_info = GenericListing(
        property_id="144595010",
        image_url="https://media.rightmove.co.uk:443/dir/crop/10:9-16:9/260k/259202/144595010"
        "/259202_THECI_005196_IMG_00_0000_max_476x317.jpeg",
        description="Lorem ipsum",
        price="£1,000 pcm",
        added_date=added_date,
        postcode="N1 1AA",
        address="123 Fake Street, N1 1AA",
    )
    assert l_info.added_date == datetime.date(2024, 2, 10)


@pytest.mark.parametrize(
    ("price", "expected"),
    [
        ("1000$", Price(price=1000, currency=Currency.USD, per=None)),
        ("$1000", Price(price=1000, currency=Currency.USD, per=None)),
        (
            "£1000 pcm",
            Price(price=1000, currency=Currency.GBP, per=PriceUnit.PER_MONTH),
        ),
        (
            "£1000 pw",
            Price(price=1000, currency=Currency.GBP, per=PriceUnit.PER_WEEK),
        ),
        ("1000£", Price(price=1000, currency=Currency.GBP, per=None)),
        ("£100,000", Price(price=100000, currency=Currency.GBP, per=None)),
        ("10000zl", Price(price=10000, currency=Currency.PLN, per=None)),
    ],
)
def test_price_parsing_simple(price: str, expected: Price) -> None:
    l_info = RightmoveRentalListing(
        property_id="144595010",
        image_url="https://media.rightmove.co.uk:443/dir/crop/10:9-16:9/260k/259202/144595010"
        "/259202_THECI_005196_IMG_00_0000_max_476x317.jpeg",
        description="Lorem ipsum",
        price=price,
        added_date="2024-02-10",
        postcode="N1 1AA",
        address="123 Fake Street, N1 1AA",
    )
    assert l_info.price == expected


@pytest.mark.skip()
@pytest.mark.parametrize(
    ("price", "expected"),
    [
        ("1000USD", Price(price=1000, currency=Currency.USD, per=None)),
        (
            "£1000.70 pcm",
            Price(price=1000, currency=Currency.GBP, per=PriceUnit.PER_MONTH),
        ),
        ("1000£", Price(price=1000, currency=Currency.GBP, per=None)),
        ("100zł", Price(price=100, currency=Currency.PLN, per=None)),
    ],
)
def test_price_parsing_complicated(price: str, expected: Price) -> None:
    l_info = RightmoveRentalListing(
        property_id="144595010",
        image_url="https://media.rightmove.co.uk:443/dir/crop/10:9-16:9/260k/259202/144595010"
        "/259202_THECI_005196_IMG_00_0000_max_476x317.jpeg",
        description="Lorem ipsum",
        price=price,
        added_date="2024-02-10",
        phone_number="123456789",
    )
    assert l_info.price == expected
