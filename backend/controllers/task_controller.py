from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.schemas.task_schema import TaskCreate, TaskResponse, TaskUpdate
from backend.services.task_services import get_tasks_for_user, create_task, delete_task, updated_task
from backend.database import SessionLocal

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/{user_id}", response_model=list[TaskResponse])
def get_tasks(user_id: int, db: Session = Depends(get_db)):
    return get_tasks_for_user(db, user_id)

@router.post("/", response_model=TaskResponse)
def add_task(task: TaskCreate, db: Session = Depends(get_db)):
    return create_task(db, task)

@router.delete("/{task_id}")
def delete_user_task(task_id: int, user_id: int, db: Session = Depends(get_db)):
    delete_task(db, task_id, user_id)
    return {"message": "Task deleted successfully."}

@router.put("/{task_id}", response_model=TaskResponse)
def update_user_task(task_id: int, user_id: int, task_data: TaskUpdate,db: Session = Depends(get_db)):
    return updated_task(db, task_id, user_id, task_data)



