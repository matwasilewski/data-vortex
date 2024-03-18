from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Float, Date, DateTime

Base = declarative_base()

class GenericListing(Base):
    __tablename__ = 'generic_listing'
    property_id = Column(String, primary_key=True)
    image_urls = Column(String)  # Stored as JSON string
    description = Column(String)
    price_amount = Column(Float)
    price_currency = Column(String)
    added_date = Column(Date)
    address = Column(String, nullable=True)
    postcode = Column(String, nullable=True)
    created_date = Column(DateTime, default=datetime.datetime.now)