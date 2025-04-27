from sqlalchemy.orm import Session
from backend.models.models import Task
from fastapi import HTTPException, status
from backend.schemas.task_schema import TaskCreate, TaskUpdate

def get_tasks_for_user(db: Session, user_id: int):
    return db.query(Task).filter(Task.user_id == user_id).all()

def create_task(db: Session, task_data: TaskCreate):
    new_task = Task(**task_data.dict())
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

def get_tasks(session: Session, user_id: int, status: str | None = None, due_date: str | None = None):
    query = session.query(Task).filter(Task.user_id == user_id)
    if status:
        query = query.filter(Task.status == status)
    if due_date:
        query = query.filter(Task.due_date == due_date)

    return query.all()    

def delete_task(session: Session, task_id:int, user_id:int) -> None:
    print("Task ID:", task_id)
    print("User ID:", user_id)
    print("Looking for task...")
    task = session.query(Task).filter_by(id=task_id,user_id=user_id).first()
    print("Task found:", task)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or access denied."
        )

    session.delete(task)
    session.commit()    

def updated_task(session:Session, task_id:int, user_id:int, task_data:TaskUpdate) -> Task: 
    task = session.query(Task).filter_by(id=task_id,user_id=user_id).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or access denied."
        )

    for field, value in task_data.dict(exclude_unset=True).items():
        setattr(task, field, value)    
    
    session.commit()
    session.refresh(task)
    return task