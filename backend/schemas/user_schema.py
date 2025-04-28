from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    password: str


class UserRead(BaseModel):
    id: int
    username: str
    password: str

    class Config:
        orm_mode = True