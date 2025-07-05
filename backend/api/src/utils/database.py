"""
Database utility module for SQLAlchemy configuration and session management.

This module provides database connection setup, session management,
and initialization functions for the TaskGPT API.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from typing import Generator
import os

engine = create_engine(os.environ["DATABASE_URL"])

Base = declarative_base()

def init_db() -> None:
    """
    Initialize the database by creating all tables.
    
    This function creates all tables defined in the models
    based on the SQLAlchemy Base class.
    """
    Base.metadata.create_all(bind=engine)

def get_db() -> Generator[Session, None, None]: 
    """
    Database session dependency for FastAPI.
    
    Yields:
        Database session object
        
    Note:
        This is a generator function that yields a database session
        and ensures proper cleanup after the request is complete.
        It should be used as a FastAPI dependency.
    """
    SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()