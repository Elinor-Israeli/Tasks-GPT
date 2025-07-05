from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from models import Task
from fastapi import HTTPException, status
from schemas.task_schema import TaskCreate
from typing import Optional, List
from datetime import datetime, date

def create_task(db: Session, task_data: TaskCreate) -> Task:
    new_task: Task = Task(**task_data.dict())

    try:
        db.add(new_task)
        db.commit()
        db.refresh(new_task)
        return new_task
    
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e.orig).lower()
        )

def get_tasks(session: Session, user_id: int, done: Optional[bool] = None, overdue: bool = False, upcoming: bool = False) -> List[Task]:
    query = session.query(Task).filter(Task.user_id == user_id)
    if done is not None:
        query = query.filter(Task.done == done)

    today: datetime = datetime.today()

    if overdue: 
        query = query.filter(
            Task.done == False,
            Task.due_date != None,
            Task.due_date < today.isoformat()
        )

    if upcoming:
        query = query.filter(
            Task.done == False,
            Task.due_date != None,
            Task.due_date > today.isoformat()
        )
    return query.order_by(Task.id.desc()).all()    

def get_task_by_id(db: Session, task_id: int) -> Optional[Task]:
    print(f"get_task_by_id querying for task_id: {task_id}")
    task: Optional[Task] = db.query(Task).filter(Task.id == task_id).first() 
    print(f"Query result: {task}")
    return task

def delete_task(session: Session, task_id: int) -> None:
    task: Optional[Task] = session.query(Task).filter_by(id=task_id).first()

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
    task: Optional[Task] = session.query(Task).filter_by(id=task_id).first()

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