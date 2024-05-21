import datetime
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping, Optional

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    HttpUrl,
    field_validator,
    model_validator,
)


class PriceUnit(Enum):
    PER_WEEK = "PER_WEEK"
    PER_MONTH = "PER_MONTH"
    PER_YEAR = "PER_YEAR"
    ONE_OFF = "ONE_OFF"


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
    model_config = ConfigDict(extra="forbid", from_attributes=True)
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

    def to_orm_dict(self):
        return {
            "property_id": self.property_id,
            "image_url": str(self.image_url),
            "description": self.description,
            "price_amount": self.price.price,
            "price_per": self.price.per.value,
            "price_currency": self.price.currency.name,
            "added_date": self.added_date,
            "address": self.address,
            "postcode": self.postcode,
            "created_date": self.created_date,
        }

    @classmethod
    def from_orm(cls, obj: Any):
        obj_dict = obj.__dict__
        return cls(
            property_id=obj_dict["property_id"],
            image_url=obj_dict["image_url"],
            description=obj_dict["description"],
            price=Price(
                price=obj_dict["price_amount"],
                currency=Currency[obj_dict["price_currency"]],
                per=PriceUnit[obj_dict["price_per"]],
            ),
            added_date=obj_dict["added_date"],
            address=obj_dict["address"],
            postcode=obj_dict["postcode"],
            created_date=obj_dict["created_date"],
        )

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
        except Exception as e:
            raise ValueError(
                f"Listing must have a price! Raw price found: {v}"
            ) from e
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

    class Config:
        extra = "forbid"


class RequestData(BaseModel):
    url: str
    _params: Optional[Mapping[str, str]] = None  # Default params to None
    _headers: Mapping[str, str]

    class Config:
        frozen = True

    def __init__(__pydantic_self__, **data):  # noqa: N805
        super().__init__(**data)
        # Convert headers to immutable type immediately upon initialization
        object.__setattr__(
            __pydantic_self__,
            "_headers",
            MappingProxyType(data.get("headers", {})),
        )
        # Only convert params to immutable type if they are provided
        if "params" in data and data["params"] is not None:
            object.__setattr__(
                __pydantic_self__, "_params", MappingProxyType(data["params"])
            )

    @property
    def params(self):
        return self._params

    @property
    def headers(self):
        return self._headers

    def __hash__(self):
        # Adjust hash to handle optional params
        params_hash = frozenset(self.params.items()) if self.params else None
        return hash(
            (
                self.url,
                params_hash,
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
