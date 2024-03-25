from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from data_vortex.database.models import Base
from data_vortex.utils.config import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_database():
    Base.metadata.create_all(bind=engine)
