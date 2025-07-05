"""
Task controller module for handling task-related HTTP requests.

This module provides REST API endpoints for task management operations
including CRUD operations and task filtering.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from schemas.task_schema import TaskCreate, TaskResponse, TaskUpdate
from services.task_services import get_task_by_id, get_tasks, create_task, delete_task, updated_task
from utils.database import get_db
from typing import Optional, List, Dict, Any

router: APIRouter = APIRouter()

@router.get("/", response_model=List[TaskResponse])
def get_tasks_route(
    user_id: int = Query(..., description="ID of the user to retrieve tasks for"),
    done: Optional[bool] = Query(None, description="Filter tasks by completion status"),
    overdue: Optional[bool] = Query(False, description="Filter overdue tasks"),
    upcoming: Optional[bool] = Query(False, description="Filter upcoming tasks"),
    db: Session = Depends(get_db)
) -> List[TaskResponse]:
    """
    Retrieve tasks for a specific user with optional filtering.
    
    Args:
        user_id: The ID of the user whose tasks to retrieve
        done: Optional filter for task completion status
        overdue: Filter for overdue tasks (default: False)
        upcoming: Filter for upcoming tasks (default: False)
        db: Database session dependency
        
    Returns:
        List of task responses matching the criteria
        
    Raises:
        HTTPException: If user is not found or database error occurs
    """
    return get_tasks(db, user_id, done=done, overdue=overdue, upcoming=upcoming)

@router.get("/{task_id}", response_model=TaskResponse)
def get_task_by_id_route(task_id: int, db: Session = Depends(get_db)) -> TaskResponse:
    """
    Retrieve a specific task by its ID.
    
    Args:
        task_id: The ID of the task to retrieve
        db: Database session dependency
        
    Returns:
        Task response object
        
    Raises:
        HTTPException: If task is not found
    """
    task = get_task_by_id(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.post("/", response_model=TaskResponse)
def add_task(task: TaskCreate, db: Session = Depends(get_db)) -> TaskResponse:
    """
    Create a new task.
    
    Args:
        task: Task creation data
        db: Database session dependency
        
    Returns:
        Created task response object
        
    Raises:
        HTTPException: If task creation fails (e.g., duplicate title)
    """
    return create_task(db, task)

@router.delete("/{task_id}")
def delete_task_route(
    task_id: int,
    db: Session = Depends(get_db)
) -> Dict[str, str]:
    """
    Delete a task by its ID.
    
    Args:
        task_id: The ID of the task to delete
        db: Database session dependency
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If task is not found
    """
    delete_task(db, task_id)
    return {"message": "Task deleted successfully."}

@router.put("/{task_id}", response_model=TaskResponse)
def update_task_route(task_id: int, task_data: TaskUpdate, db: Session = Depends(get_db)) -> TaskResponse:
    """
    Update an existing task.
    
    Args:
        task_id: The ID of the task to update
        task_data: Updated task data
        db: Database session dependency
        
    Returns:
        Updated task response object
        
    Raises:
        HTTPException: If task is not found
    """
    print(f"Received update for task {task_id}: {task_data}")
    return updated_task(
        session=db,
        task_id=task_id,
        title=task_data.title,
        done=task_data.done,
        due_date=task_data.due_date,
    )
