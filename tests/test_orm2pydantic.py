import datetime

from data_vortex.database.models import RentalListing
from data_vortex.rightmove_models import RightmoveRentalListing, Price, Currency, PriceUnit


def test_load_orm_from_dict() -> None:
    rl = {
        "property_id": "123",
        "image_url": "https://media.rightmove.co.uk:443/dir/crop/10:9-16:9/260k/259202/144595010"
        "/259202_THECI_005196_IMG_00_0000_max_476x317.jpeg",
        "description": "Lorem ipsum",
        "price_amount": 1000,
        "price_per": "per_month",
        "price_currency": "GBP",
        "added_date": datetime.date(2024, 2, 10),
        "address": "123 Fake Street, N1 1AA",
        "postcode": "N1 1AA",
        "created_date": datetime.date(2024, 1, 10),
    }
    rl2 = RentalListing(**rl)
    assert rl2.property_id == "123"
    assert rl2.image_url == "https://media.rightmove.co.uk:443/dir/crop/10:9-16:9/260k/259202/144595010" \
                             "/259202_THECI_005196_IMG_00_0000_max_476x317.jpeg"
    assert rl2.description == "Lorem ipsum"
    assert rl2.price_amount == 1000
    assert rl2.price_per == "per_month"
    assert rl2.price_currency == "GBP"
    assert rl2.added_date == datetime.date(2024, 2, 10)
    assert rl2.address == "123 Fake Street, N1 1AA"
    assert rl2.postcode == "N1 1AA"
    assert rl2.created_date == datetime.date(2024, 1, 10)



def test_rightmove_to_orm_export():
    listing = RightmoveRentalListing(
        property_id="144595010",
        image_url="https://media.rightmove.co.uk:443/dir/crop/10:9-16:9/260k/259202/144595010"
        "/259202_THECI_005196_IMG_00_0000_max_476x317.jpeg",
        description="Lorem ipsum",
        price=Price(price=1000, currency=Currency.GBP, per=PriceUnit.PER_MONTH),
        added_date="2024-02-10",
        address="123 Fake Street, N1 1AA",
        postcode="N1 1AA",
    )
    orm_dict = listing.to_orm_dict()

    assert orm_dict == {
        "property_id": "144595010",
        "image_url": "https://media.rightmove.co.uk:443/dir/crop/10:9-16:9/260k/259202/144595010"
        "/259202_THECI_005196_IMG_00_0000_max_476x317.jpeg",
        "description": "Lorem ipsum",
        "price_amount": 1000,
        "price_per": "per_month",
        "price_currency": "GBP",
        "added_date": datetime.date(2024, 2, 10),
        "address": "123 Fake Street, N1 1AA",
        "postcode": "N1 1AA",
        "created_date": None,
    }