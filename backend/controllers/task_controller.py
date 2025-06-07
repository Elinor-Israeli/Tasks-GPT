from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from backend.schemas.task_schema import TaskCreate, TaskResponse, TaskUpdate
from backend.services.task_services import  get_task_by_id, get_tasks, create_task, delete_task, updated_task
from backend.services.database import get_db
from typing import Optional

router = APIRouter()

@router.get("/", response_model=list[TaskResponse])
def get_tasks_route(
    user_id: int = Query(..., description="ID of the user to retrieve tasks for"),
    done: Optional[bool] = Query(None, description="Filter tasks by completion status"),
    due_date: Optional[str] = Query(None, description="Filter tasks by due date (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    return get_tasks(db, user_id, done=done, due_date=due_date)

@router.get("/{task_id}", response_model=TaskResponse)
def get_task_by_id_route(task_id: int, db: Session = Depends(get_db)):
    task = get_task_by_id(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.post("/", response_model=TaskResponse)
def add_task(task: TaskCreate, db: Session = Depends(get_db)):
    return create_task(db, task)

@router.delete("/{task_id}")
def delete_task_route(
    task_id: int,
    user_id: int = Query(..., description="ID of the user deleting the task"),
    db: Session = Depends(get_db)
):
    delete_task(db, task_id, user_id)
    return {"message": "Task deleted successfully."}

@router.put("/{task_id}", response_model=TaskResponse)
def update_task_route(task_id: int, task_data: TaskUpdate, db: Session = Depends(get_db)):
    print(f"Received update for task {task_id}: {task_data}")
    return updated_task(
        session=db,
        task_id=task_id,
        title=task_data.title,
        done=task_data.done,
        due_date=task_data.due_date,
    )
