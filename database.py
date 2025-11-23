from models import Base

from sqlalchemy import create_engine

from sqlalchemy.orm import sessionmaker

import os

DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql+psycopg2://yrii:secretpass@localhost:8000/prdb"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
