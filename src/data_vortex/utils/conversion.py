from pydantic_core import Url

from src.data_vortex.database.models import RentalListing
from src.data_vortex.rightmove_models import (
    Currency,
    Price,
    PriceUnit,
    RightmoveRentalListing,
)


def orm2pydantic_rental_listing(
    orm_rental_listing: RentalListing,
) -> RightmoveRentalListing:
    return RightmoveRentalListing(
        property_id=orm_rental_listing.property_id,
        image_url=Url(orm_rental_listing.image_url)
        if orm_rental_listing.image_url != "None"
        else None,
        description=orm_rental_listing.description,
        price=Price(
            price=orm_rental_listing.price_amount,
            currency=Currency[orm_rental_listing.price_currency],
            per=PriceUnit[orm_rental_listing.price_per],
        ),
        added_date=orm_rental_listing.added_date,
        address=orm_rental_listing.address,
        postcode=orm_rental_listing.postcode,
        created_date=orm_rental_listing.created_date,
    )
