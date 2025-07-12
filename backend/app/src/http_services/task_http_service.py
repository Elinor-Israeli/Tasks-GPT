"""
Task HTTP service module for task-related API operations.

This module provides a service layer for making task-related HTTP requests
to the TaskGPT API with proper error handling and data formatting.
"""

from typing import Optional, Dict, Any, List
from .http_client import HttpClient


class TaskHttpService:
    """
    HTTP service for task-related API operations.
    
    This class provides methods for all task-related HTTP requests
    including CRUD operations and filtering.
    
    Attributes:
        client: HTTP client for making requests
    """
    
    def __init__(self, client: HttpClient) -> None:
        self.client: HttpClient = client

    async def get_tasks(
            self, 
            user_id: int, 
            done: Optional[bool] = None, 
            overdue: bool = False, 
            upcoming: bool = False,
            date: Optional[str] = None,
            start_date: Optional[str] = None,
            end_date: Optional[str] = None
        ) -> List[Dict[str, Any]]:
        """
        Retrieve tasks for a user with optional filtering.
        
        Args:
            user_id: ID of the user whose tasks to retrieve
            done: Optional filter for completion status
            overdue: Filter for overdue tasks
            upcoming: Filter for upcoming tasks
            date: Filter for exact due date
            start_date: Start of date range (inclusive)
            end_date: End of date range (inclusive)
            
        Returns:
            List of task dictionaries
            
        Raises:
            httpx.HTTPStatusError: If the request fails
        """
        params: Dict[str, Any] = {"user_id": user_id}

        if done is not None:
            params["done"] = done

        if overdue:
            params["overdue"] = True

        if upcoming:
            params["upcoming"] = True

        if date:
            params["date"]

        if start_date:
            params["start_date"]      

        if end_date:
            params["end_date"]      

        response = await self.client.get("/tasks/", params=params)
        response.raise_for_status()
        return response.json()

    async def get_task_by_id(self, task_id: int) -> Dict[str, Any]:
        """
        Retrieve a specific task by its ID.
        
        Args:
            task_id: ID of the task to retrieve
            
        Returns:
            Task dictionary
            
        Raises:
            httpx.HTTPStatusError: If the request fails
        """
        response = await self.client.get(f"/tasks/{task_id}")
        response.raise_for_status()
        return response.json()

    async def create_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new task.
        
        Args:
            task_data: Task data including title, due_date, user_id
            
        Returns:
            Created task dictionary
            
        Raises:
            httpx.HTTPStatusError: If the request fails
        """
        response = await self.client.post("/tasks/", json=task_data)
        return response.json()

    async def update_task(self, task_id: int, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing task.
        
        Args:
            task_id: ID of the task to update
            task_data: Updated task data
            
        Returns:
            Updated task dictionary
            
        Raises:
            httpx.HTTPStatusError: If the request fails
        """
        response = await self.client.put(f"/tasks/{task_id}", json=task_data)
        response.raise_for_status()
        return response.json()

    async def delete_task(self, task_id: int) -> bool:
        """
        Delete a task by its ID.
        
        Args:
            task_id: ID of the task to delete
            
        Returns:
            True if deletion was successful
            
        Raises:
            httpx.HTTPStatusError: If the request fails
        """
        response = await self.client.delete(f"/tasks/{task_id}")
        response.raise_for_status()
        return response.status_code == 204
    
    async def close(self) -> None:
        """
        Close the HTTP client.
        """
        await self.client.aclose()

