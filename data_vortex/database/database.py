from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base  # Import the Base from models.py

DATABASE_URL = "sqlite:///listings.db"  # Or another database URL

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)