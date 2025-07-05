"""
HTTP client module for making API requests.

This module provides a wrapper around httpx for making HTTP requests
to the TaskGPT API with proper error handling and timeout configuration.
"""

import httpx
import os
from typing import Optional, Dict, Any

class HttpClient:
    """
    HTTP client for making API requests to the TaskGPT backend.
    
    This class provides a simplified interface for making HTTP requests
    with proper timeout handling and error management.
    
    Attributes:
        client: Underlying httpx AsyncClient instance
    """
    
    def __init__(self, base_url: Optional[str] = None) -> None:
        base_url = base_url or os.getenv("API_BASE_URL" , "http://localhost:8000")
        self.client: httpx.AsyncClient = httpx.AsyncClient(base_url=base_url, timeout=10.0)

    async def get(self, url: str, params: Optional[Dict[str, Any]] = None, **kwargs) -> httpx.Response:
        """
        Make a GET request.
        
        Args:
            url: Endpoint URL (relative to base_url)
            params: Query parameters
            **kwargs: Additional arguments passed to httpx
            
        Returns:
            HTTP response object
        """
        return await self.client.get(url, params=params, **kwargs)

    async def post(self, url: str, **kwargs) -> httpx.Response:
        """
        Make a POST request.
        
        Args:
            url: Endpoint URL (relative to base_url)
            **kwargs: Additional arguments passed to httpx
            
        Returns:
            HTTP response object
        """
        return await self.client.post(url, **kwargs)

    async def put(self, url: str, **kwargs) -> httpx.Response:
        """
        Make a PUT request.
        
        Args:
            url: Endpoint URL (relative to base_url)
            **kwargs: Additional arguments passed to httpx
            
        Returns:
            HTTP response object
        """
        return await self.client.put(url, **kwargs)

    async def delete(self, url: str) -> httpx.Response:
        """
        Make a DELETE request.
        
        Args:
            url: Endpoint URL (relative to base_url)
            
        Returns:
            HTTP response object
        """
        return await self.client.delete(url)

    async def close(self) -> None:
        """
        Close the HTTP client and free resources.
        """
        await self.client.aclose()
