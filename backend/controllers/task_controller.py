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
    overdue: Optional[bool] = Query(False, description="Filter overdue tasks"),
    upcoming: Optional[bool] = Query(False, description="Filter upcoming tasks"),
    db: Session = Depends(get_db)
):
    return get_tasks(db, user_id, done=done, overdue=overdue, upcoming=upcoming)

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
    db: Session = Depends(get_db)
):
    delete_task(db, task_id)
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
