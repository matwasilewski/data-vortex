from sqlalchemy.orm import Session
import json

from data_vortex.database.models import DbListing
from data_vortex.rightmove_models import GenericListing


def create_listing(db: Session, db_listing: DbListing):
    db.add(db_listing)
    db.commit()
    db.refresh(db_listing)
    return db_listing


def get_listing(db: Session, property_id: str):
    return db.query(DbListing).filter(GenericListing.property_id == property_id).first()
