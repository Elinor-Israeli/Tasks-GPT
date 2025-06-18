from sqlalchemy.orm import Session
from backend.api.models import User
from backend.api.schemas.user_schema import UserCreate
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password:str):
    return pwd_context.hash(password)

def create_user(db: Session, user_create: UserCreate):
    hashed_pw = hash_password(user_create.password)
    new_user = User(username=user_create.username, password=hashed_pw)
    print('create_new_user', new_user)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_all_users(db: Session):
    return db.query(User).all()

def delete_user(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        db.delete(user)
        db.commit()
    return user
