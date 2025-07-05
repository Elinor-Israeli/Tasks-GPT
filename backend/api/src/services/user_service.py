"""
User service module for user operations.

This module contains user management actions including
user creation, authentication, and data validation.
"""

from sqlalchemy.orm import Session
from models import User
from schemas.user_schema import UserCreate
from passlib.context import CryptContext
from typing import Optional, List

pwd_context: CryptContext = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.
    
    Args:
        password: Plain text password to hash
        
    Returns:
        Hashed password string
    """
    return pwd_context.hash(password)

def create_user(db: Session, user_create: UserCreate) -> User:
    """
    Create a new user in the database.
    
    Args:
        db: Database session
        user_create: User creation data containing username and password
        
    Returns:
        Created user object
        
    Raises:
        HTTPException: If user creation fails due to integrity constraints
                      (e.g., duplicate username)
    """
    hashed_pw: str = hash_password(user_create.password)
    new_user: User = User(username=user_create.username, password=hashed_pw)
    print('create_new_user', new_user)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

def get_user(db: Session, user_id: int) -> Optional[User]:
    """
    Retrieve a specific user by their ID.
    
    Args:
        db: Database session
        user_id: ID of the user to retrieve
        
    Returns:
        User object if found, None otherwise
    """
    return db.query(User).filter(User.id == user_id).first()

def get_all_users(db: Session) -> List[User]:
    """
    Retrieve all users from the database.
    
    Args:
        db: Database session
        
    Returns:
        List of all user objects
    """
    return db.query(User).all()

def delete_user(db: Session, user_id: int) -> Optional[User]:
    """
    Delete a user by their ID.
    
    Args:
        db: Database session
        user_id: ID of the user to delete
        
    Returns:
        Deleted user object if found, None otherwise
    """
    user: Optional[User] = db.query(User).filter(User.id == user_id).first()
    if user:
        db.delete(user)
        db.commit()
    return user
