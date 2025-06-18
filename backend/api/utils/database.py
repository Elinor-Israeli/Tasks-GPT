from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

engine = create_engine(os.environ["DATABASE_URL"])

Base = declarative_base()

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db(): 
    SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()