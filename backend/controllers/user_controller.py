from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.services.user_service import create_user, get_user, get_all_users, delete_user
from backend.schemas.user_schema import UserCreate, UserRead
from backend.services.database import get_db
from backend.models.models import User

router = APIRouter() 

@router.post("/", response_model=UserRead)
def add_user(user_create: UserCreate, db: Session = Depends(get_db)):
    return create_user(db, user_create)

@router.get("/{user_id}", response_model=UserRead)
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = get_user(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/", response_model=list[UserRead])
def read_users(db: Session = Depends(get_db)):
    return get_all_users(db)

@router.get("/by-username/{username}")
def get_user_by_username(username: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.delete("/{user_id}", response_model=UserRead)
def delete_existing_user(user_id: int, db: Session = Depends(get_db)):
    user = delete_user(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user
