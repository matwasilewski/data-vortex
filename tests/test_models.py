import datetime

import pytest

from data_vortex.models import ListingInfo, Price


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
    l_info = ListingInfo(
        property_id="144595010",
        image_urls=[
            "https://media.rightmove.co.uk:443/dir/crop/10:9-16:9/260k/259202/144595010"
            "/259202_THECI_005196_IMG_00_0000_max_476x317.jpeg"
        ],
        description="Lorem ipsum",
        price="£1,000 pcm",
        added_date=added_date,
        phone_number="123456789",
    )
    assert l_info.added_date == datetime.date(2024, 2, 10)


def test_date_parsing_2() -> None:
    l_info = ListingInfo(
        property_id="144595010",
        image_urls=[
            "https://media.rightmove.co.uk:443/dir/crop/10:9-16:9/260k/259202/144595010"
            "/259202_THECI_005196_IMG_00_0000_max_476x317.jpeg"
        ],
        description="Lorem ipsum",
        price="£1,000 pcm",
        added_date="2024-02-10",
        phone_number="123456789",
    )
    assert l_info.added_date == datetime.date(2024, 2, 10)


def test_price_parsing_gbp() -> None:
    l_info = ListingInfo(
        property_id="144595010",
        image_urls=[
            "https://media.rightmove.co.uk:443/dir/crop/10:9-16:9/260k/259202/144595010"
            "/259202_THECI_005196_IMG_00_0000_max_476x317.jpeg"
        ],
        description="Lorem ipsum",
        price="£1,000 pcm",
        added_date="2024-02-10",
        phone_number="123456789",
    )
    assert l_info.price == Price(price=1000.0, currency="GBP", per="pcm")
