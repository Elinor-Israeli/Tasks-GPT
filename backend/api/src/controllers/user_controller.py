"""
User controller module for handling user-related HTTP requests.

This module provides REST API endpoints for user management operations
including user creation, retrieval, and deletion.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from services.user_service import create_user, get_user, get_all_users, delete_user
from schemas.user_schema import UserCreate, UserRead
from utils.database import get_db
from models import User
from typing import List, Optional

router: APIRouter = APIRouter() 

@router.post("/", response_model=UserRead)
def add_user(user_create: UserCreate, db: Session = Depends(get_db)) -> UserRead:
    """
    Create a new user account.
    
    Args:
        user_create: User creation data containing username and password
        db: Database session dependency
        
    Returns:
        Created user response object
        
    Raises:
        HTTPException: If user creation fails (e.g., duplicate username)
    """
    return create_user(db, user_create)

@router.get("/{user_id}", response_model=UserRead)
def read_user(user_id: int, db: Session = Depends(get_db)) -> UserRead:
    """
    Retrieve a specific user by their ID.
    
    Args:
        user_id: The ID of the user to retrieve
        db: Database session dependency
        
    Returns:
        User response object
        
    Raises:
        HTTPException: If user is not found
    """
    user: Optional[User] = get_user(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/", response_model=List[UserRead])
def read_users(db: Session = Depends(get_db)) -> List[UserRead]:
    """
    Retrieve all users in the system.
    
    Args:
        db: Database session dependency
        
    Returns:
        List of all user response objects
    """
    return get_all_users(db)

@router.get("/by-username/{username}")
def get_user_by_username(username: str, db: Session = Depends(get_db)) -> UserRead:
    """
    Retrieve a user by their username.
    
    Args:
        username: The username to search for
        db: Database session dependency
        
    Returns:
        User object if found
        
    Raises:
        HTTPException: If user is not found
    """
    user: Optional[User] = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.delete("/{user_id}", response_model=UserRead)
def delete_existing_user(user_id: int, db: Session = Depends(get_db)) -> UserRead:
    """
    Delete a user by their ID.
    
    Args:
        user_id: The ID of the user to delete
        db: Database session dependency
        
    Returns:
        Deleted user response object
        
    Raises:
        HTTPException: If user is not found
    """
    user: Optional[User] = delete_user(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user
