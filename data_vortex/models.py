import datetime
from enum import Enum
from typing import List, Optional, Dict

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator


class PriceUnit(Enum):
    PER_WEEK = "per_week"
    PER_MONTH = "per_month"
    PER_YEAR = "per_year"
    ONE_OFF = "one_off"


class Currency(Enum):
    GBP = "£"
    USD = "$"
    PLN = "zl"


class Price(BaseModel):
    price: int
    currency: Optional[Currency]
    per: Optional[PriceUnit]


# noinspection PyNestedDecorators
class GenericListing(BaseModel):
    model_config = ConfigDict(extra="forbid")

    property_id: str
    image_urls: List[HttpUrl]
    description: str
    price: Price
    added_date: datetime.date
    created_date: datetime.datetime = Field(
        default_factory=datetime.datetime.now
    )
    _default_currency: Optional[Currency] = None
    _default_price_unit: Optional[PriceUnit] = None

    @field_validator("property_id")
    @classmethod
    def property_id_is_not_zero(cls, v: str) -> str:
        "Empty listings on rightmove are listed with zero. This is not a valid property id."
        if v == "0":
            raise ValueError("ID must not be zero!")
        return v

    @field_validator("added_date", mode="before")
    @classmethod
    def parse_added_date(cls, v: str) -> datetime.date:
        if isinstance(v, datetime.date):
            return v
        elif isinstance(v, datetime.datetime):
            return v.date()
        elif not isinstance(v, str):
            raise ValueError("Invalid date format")
        elif v.startswith("Added on "):
            date_str = v.replace("Added on ", "")
        else:
            date_str = v

        for date_format in ["%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%Y/%m/%d"]:
            try:
                return datetime.datetime.strptime(date_str, date_format).date()
            except ValueError:
                pass
        raise ValueError("Invalid date format")

    @field_validator("price", mode="before")
    @classmethod
    def parse_price(cls, v: str):
        # Initialize variables
        amount = 0
        currency = None
        per = None

        # Check for currency and remove it from the string
        for cur in Currency:
            if cur.value in v:
                currency = cur
                v = v.replace(cur.value, "")
                break

        # Check for pricing frequency
        if "pcm" in v:
            per = PriceUnit.PER_MONTH
            v = v.replace("pcm", "")
        elif "pw" in v:
            per = PriceUnit.PER_WEEK
            v = v.replace("pw", "")

        # Remove any commas and convert to integer
        amount = int(v.replace(",", ""))

        # Return a Price instance
        return Price(price=amount, currency=currency, per=per)


class RightmoveRentalListing(GenericListing):
    _default_currency: Currency = Currency.GBP
    _default_price_unit: PriceUnit = PriceUnit.PER_MONTH


class RightmoveSaleListing(GenericListing):
    _default_currency: Currency = Currency.GBP
    _default_price_unit: PriceUnit = PriceUnit.ONE_OFF


class RequestData(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    url: str
    params: Dict[str, str]
    headers: Dict[str, str]


class RightmoveRentParams(BaseModel):
    searchType: str = "RENT"
    locationIdentifier: str = "REGION^87490"  # London
    insId: str = "1"
    radius: str = "0.0"
    minPrice: str = ""
    maxPrice: str = ""
    minBedrooms: str = ""
    maxBedrooms: str = ""
    displayPropertyType: str = ""
    maxDaysSinceAdded: str = ""
    sortByPriceDescending: str = ""
    _includeLetAgreed: str = "on"
    primaryDisplayPropertyType: str = ""
    secondaryDisplayPropertyType: str = ""
    oldDisplayPropertyType: str = ""
    oldPrimaryDisplayPropertyType: str = ""
    letType: str = ""
    letFurnishType: str = ""
    houseFlatShare: str = ""
