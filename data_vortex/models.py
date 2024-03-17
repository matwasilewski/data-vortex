from typing import List

from pydantic import BaseModel


class ListingInfo(BaseModel):
    property_id: str
    image_urls: List[str]
    description: str
    price: str
    added_date: str
    phone_number: str
