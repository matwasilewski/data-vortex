from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from data_vortex.database.models import Base

DATABASE_URL = "sqlite:///vortex.db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_database():
    Base.metadata.create_all(bind=engine)
