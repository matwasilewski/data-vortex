import datetime

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Float, Date, DateTime

Base = declarative_base()

class DbListing(Base):
    __tablename__ = 'rental_listings'
    property_id = Column(String, primary_key=True)
    image_url = Column(String, nullable=True)
    description = Column(String)
    price_amount = Column(Float)
    price_currency = Column(String, nullable=True)
    added_date = Column(Date)
    address = Column(String, nullable=True)
    postcode = Column(String, nullable=True)
    created_date = Column(DateTime, default=datetime.datetime.now)