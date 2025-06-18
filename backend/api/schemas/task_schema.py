from pydantic import BaseModel
from datetime import date
from typing import Optional

class TaskCreate(BaseModel):
    title: str
    due_date: Optional[date] = None
    done: Optional[bool] = False
    user_id: int

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done:Optional[bool] = None
    due_date: Optional[date] = None
    
     
class TaskResponse(TaskCreate):
    id: int
    user_id: int

    class Config:
        orm_mode = True
