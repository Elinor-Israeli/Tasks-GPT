from sqlalchemy.orm import Session
from backend.models.models import Task
from fastapi import HTTPException, status
from backend.schemas.task_schema import TaskCreate, TaskUpdate
from typing import Optional

def create_task(db: Session, task_data: TaskCreate):
    new_task = Task(**task_data.dict())
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

def get_tasks(session: Session, user_id: int, done: bool | None = None, due_date: str | None = None):
    query = session.query(Task).filter(Task.user_id == user_id)
    if done is not None:
        query = query.filter(Task.done == done)
    if due_date:
        query = query.filter(Task.due_date == due_date)

    return query.all()    

def get_task_by_id(db: Session, task_id: int):
    print(f"get_task_by_id querying for task_id: {task_id}")
    task = db.query(Task).filter(Task.id == task_id).first() 
    print(f"Query result: {task}")
    return task

def delete_task(session: Session, task_id:int, user_id:int) -> None:
    task = session.query(Task).filter_by(id=task_id).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or access denied."
        )

    session.delete(task)
    session.commit()    

def updated_task(
    session: Session,
    task_id: int,
    title: Optional[str] = None,
    done: Optional[bool] = None,
    due_date: Optional[str] = None,
) -> Task:
    task = session.query(Task).filter_by(id=task_id).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found."
        )

    if title is not None:
        task.title = title
    if done is not None:
        task.done = done
    if due_date is not None:
        task.due_date = due_date

    session.commit()
    session.refresh(task)
    return task