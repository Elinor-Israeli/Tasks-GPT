"""
Task service module for business logic related to task operations.

This module contains the CRUD operations, filtering, and data validation.
"""

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from models import Task
from fastapi import HTTPException, status
from schemas.task_schema import TaskCreate
from typing import Optional, List
from datetime import datetime, date

def create_task(db: Session, task_data: TaskCreate) -> Task:
    """
    Create a new task in the database.
    
    Args:
        db: Database session
        task_data: Task creation data containing title, due_date, done status, and user_id
        
    Returns:
        Created task object
        
    Raises:
        HTTPException: If task creation fails due to integrity constraints
                      (e.g., duplicate title, invalid user_id)
    """
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
    """
    Retrieve tasks for a specific user with optional filtering.
    
    Args:
        session: Database session
        user_id: ID of the user whose tasks to retrieve
        done: Optional filter for task completion status (True/False/None for all)
        overdue: Filter for overdue tasks (default: False)
        upcoming: Filter for upcoming tasks (default: False)
        
    Returns:
        List of task objects matching the criteria, ordered by ID descending
        
    Note:
        Overdue tasks are those with due_date < today and done = False
        Upcoming tasks are those with due_date > today and done = False
    """
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
    """
    Retrieve a specific task by its ID.
    
    Args:
        db: Database session
        task_id: ID of the task to retrieve
        
    Returns:
        Task object if found, None otherwise
    """
    print(f"get_task_by_id querying for task_id: {task_id}")
    task: Optional[Task] = db.query(Task).filter(Task.id == task_id).first() 

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or access denied."
        )

    print(f"Query result: {task}")
    return task

def delete_task(session: Session, task_id: int) -> None:
    """
    Delete a task by its ID.
    
    Args:
        session: Database session
        task_id: ID of the task to delete
        
    Raises:
        HTTPException: If task is not found
    """
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
    """
    Update an existing task with new values.
    
    Args:
        session: Database session
        task_id: ID of the task to update
        title: New title (optional)
        done: New completion status (optional)
        due_date: New due date (optional)
        
    Returns:
        Updated task object
        
    Raises:
        HTTPException: If task is not found
    """
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