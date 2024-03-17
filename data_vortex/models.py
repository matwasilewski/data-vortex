from typing import List

from pydantic import BaseModel, field_validator


# noinspection PyNestedDecorators
class ListingInfo(BaseModel):
    property_id: str
    image_urls: List[str]
    description: str
    price: str
    added_date: str
    phone_number: str

    @field_validator('property_id')
    @classmethod
    def property_id_is_not_zero(cls, v: str) -> str:
        "Empty listings on rightmove are listed with zero. This is not a valid property id."
        if v == '0':
            raise ValueError('ID must not be zero!')
        return v