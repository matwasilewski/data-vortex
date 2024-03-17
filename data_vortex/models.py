import datetime
from enum import Enum
from typing import List

from pydantic import BaseModel, HttpUrl, field_validator


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
    currency: Currency
    per: PriceUnit


# noinspection PyNestedDecorators
class ListingInfo(BaseModel):
    property_id: str
    image_urls: List[HttpUrl]
    description: str
    price: Price
    added_date: datetime.date

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
    def parse_price(cls, v: str) -> Price:
        price_str, _, frequency = v.partition(" ")
        amount = float(
            price_str[1:].replace(",", "")
        )  # Remove currency symbol and commas
        currency_symbol = price_str[0]
        currency = Currency(currency_symbol)
        per = (
            PriceUnit.PER_MONTH if "pcm" in frequency else PriceUnit.PER_WEEK
        )  # Simplified logic, adjust as needed

        return Price(price=amount, currency=currency, per=per)
