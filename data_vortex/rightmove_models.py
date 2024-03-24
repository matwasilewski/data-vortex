import datetime
from enum import Enum
from types import MappingProxyType
from typing import Mapping, Optional

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    HttpUrl,
    field_validator,
    model_validator,
)


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
    image_url: Optional[HttpUrl] = None
    description: str
    price: Price
    added_date: datetime.date
    address: Optional[str]
    postcode: Optional[str]
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
        elif v.startswith("Reduced on "):
            date_str = v.replace("Reduced on ", "")
        elif v.startswith("Added today") or v.startswith("Reduced today"):
            return datetime.date.today()
        elif v.startswith("Added yesterday") or v.startswith(
            "Reduced yesterday"
        ):
            return datetime.date.today() - datetime.timedelta(days=1)
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
        currency = None
        per = None

        if isinstance(v, Price):
            return v
        elif isinstance(v, dict):
            return Price(**v)

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
        try:
            amount = int(v.replace(",", ""))
        except:
            pass
        # Return a Price instance
        return Price(price=amount, currency=currency, per=per)

    @model_validator(mode="after")
    def check_address_and_postcode_match(self) -> "GenericListing":
        if (
            self.address is not None
            and self.postcode is not None
            and self.postcode not in self.address
        ):
            raise ValueError("Address must contain postcode!")
        return self


class RightmoveRentalListing(GenericListing):
    _default_currency: Currency = Currency.GBP
    _default_price_unit: PriceUnit = PriceUnit.PER_MONTH


class RightmoveSaleListing(GenericListing):
    _default_currency: Currency = Currency.GBP
    _default_price_unit: PriceUnit = PriceUnit.ONE_OFF


class RightmoveRentParams(BaseModel):
    searchType: str = "RENT"  # noqa: N815
    locationIdentifier: str = "REGION^87490"  # noqa: N815
    insId: str = "1"  # noqa: N815
    index: Optional[int] = None
    radius: str = "0.0"
    minPrice: str = ""  # noqa: N815
    maxPrice: str = ""  # noqa: N815
    minBedrooms: str = ""  # noqa: N815
    maxBedrooms: str = ""  # noqa: N815
    displayPropertyType: str = ""  # noqa: N815
    maxDaysSinceAdded: str = ""  # noqa: N815
    sortByPriceDescending: str = ""  # noqa: N815
    _includeLetAgreed: str = "on"  # noqa: N815
    primaryDisplayPropertyType: str = ""  # noqa: N815
    secondaryDisplayPropertyType: str = ""  # noqa: N815
    oldDisplayPropertyType: str = ""  # noqa: N815
    oldPrimaryDisplayPropertyType: str = ""  # noqa: N815
    letType: str = ""  # noqa: N815
    letFurnishType: str = ""  # noqa: N815
    houseFlatShare: str = ""  # noqa: N815


class RequestData(BaseModel):
    url: str
    _params: Mapping[str, str]
    _headers: Mapping[str, str]

    class Config:
        frozen = True

    def __init__(__pydantic_self__, **data):
        super().__init__(**data)
        # Convert params and headers to immutable types immediately upon initialization
        object.__setattr__(
            __pydantic_self__, "_params", MappingProxyType(data["params"])
        )
        object.__setattr__(
            __pydantic_self__, "_headers", MappingProxyType(data["headers"])
        )

    @property
    def params(self):
        return self._params

    @property
    def headers(self):
        return self._headers

    def __hash__(self):
        # Ensure all parts of the hash are immutable
        return hash(
            (
                self.url,
                frozenset(self.params.items()),
                frozenset(self.headers.items()),
            )
        )

    def __eq__(self, other):
        if not isinstance(other, RequestData):
            return NotImplemented
        return (self.url, self.params, self.headers) == (
            other.url,
            other.params,
            other.headers,
        )
