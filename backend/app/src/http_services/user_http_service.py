"""
User HTTP service module for user-related API operations.

This module provides a service layer for making user-related HTTP requests
to the TaskGPT API with proper error handling and data formatting.
"""

from typing import Optional, Dict, Any
from .http_client import HttpClient

class UserHttpService:
    """
    HTTP service for user-related API operations.
    
    This class provides methods for all user-related HTTP requests
    including user creation, retrieval, and authentication.
    
    Attributes:
        client: HTTP client for making requests
    """
    
    def __init__(self, client: Optional[HttpClient] = None) -> None:
        self.client: HttpClient = client or HttpClient()

    async def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a user by their username.
        
        Args:
            username: Username to search for
            
        Returns:
            User dictionary if found, None otherwise
            
        Raises:
            httpx.HTTPStatusError: If the request fails
        """
        response = await self.client.get(f"/users/by-username/{username}")
        if response.status_code == 200:
            return response.json()
        return None

    async def get_user(self, user_id: int) -> Dict[str, Any]:
        """
        Retrieve a user by their ID.
        
        Args:
            user_id: ID of the user to retrieve
            
        Returns:
            User dictionary
            
        Raises:
            httpx.HTTPStatusError: If the request fails
        """
        response = await self.client.get(f"/users/{user_id}")
        response.raise_for_status()
        return response.json()

    async def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new user account.
        
        Args:
            user_data: User data including username and password
            
        Returns:
            Created user dictionary
            
        Raises:
            httpx.HTTPStatusError: If the request fails
        """
        response = await self.client.post("/users/", json=user_data)
        response.raise_for_status()
        return response.json()

    async def update_user(self, user_id: int, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing user.
        
        Args:
            user_id: ID of the user to update
            user_data: Updated user data
            
        Returns:
            Updated user dictionary
            
        Raises:
            httpx.HTTPStatusError: If the request fails
        """
        response = await self.client.put(f"/users/{user_id}", json=user_data)
        response.raise_for_status()
        return response.json()

    async def delete_user(self, user_id: int) -> bool:
        """
        Delete a user by their ID.
        
        Args:
            user_id: ID of the user to delete
            
        Returns:
            True if deletion was successful
            
        Raises:
            httpx.HTTPStatusError: If the request fails
        """
        response = await self.client.delete(f"/users/{user_id}")
        response.raise_for_status()
        return response.status_code == 204

    async def close(self) -> None:
        """
        Close the HTTP client.
        """
        await self.client.aclose()