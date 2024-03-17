import datetime
from enum import Enum
from typing import List

from pydantic import BaseModel, field_validator, HttpUrl, validator


# noinspection PyNestedDecorators
class ListingInfo(BaseModel):
    property_id: str
    image_urls: List[HttpUrl]
    description: str
    price: str
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
        if v.startswith("Added on "):
            date_str = v.replace("Added on ", "")
            return datetime.datetime.strptime(date_str, "%d/%m/%Y").date()
        raise ValueError("Invalid added date format")



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
    price: str
    currency: str
    per: PriceUnit
