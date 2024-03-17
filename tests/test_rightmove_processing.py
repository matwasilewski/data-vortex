import datetime
from pathlib import Path

import pytest
from bs4 import BeautifulSoup
from pydantic import HttpUrl

from data_vortex.models import Currency, Price, PriceUnit
from data_vortex.rightmove_processing import get_listings


@pytest.fixture()
def rightmove_sample(test_resources_root: Path) -> BeautifulSoup:
    sample_path = test_resources_root / "rightmove_sampe.xml"
    return BeautifulSoup(sample_path.read_text(), "html.parser")


def test_get_listings(rightmove_sample: BeautifulSoup) -> None:
    listings = get_listings(rightmove_sample)
    assert len(listings) == 1
    assert listings[0].property_id == "144595010"
    assert listings[0].image_urls == [
        HttpUrl(
            "https://media.rightmove.co.uk:443/dir/crop/10:9-16:9/260k/259202/144595010"
            "/259202_THECI_005196_IMG_00_0000_max_476x317.jpeg"
        ),
    ]
    assert (
        listings[0].description
        == "A fully furnished double bedroom is available for couples with balcony in a four-bedroom with one "
        "bathroom house-share. This property is conveniently situated in zone 2, providing excellent "
        "transportation connections to central London, with easy access to Upper Holloway station nearby."
    )
    assert listings[0].price == Price(
        price=1127.0, currency=Currency.GBP, per=PriceUnit.PER_MONTH
    )
    assert listings[0].added_date == datetime.date(2024, 2, 10)
