"""
Vector store interfaces module for the TaskGPT application.

This module defines abstract base classes for vector store operations
including adding, searching, and removing task embeddings.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any

class AddableVectorStore(ABC):
    """
    Abstract base class for vector stores that support adding embeddings.
    
    This interface defines the contract for adding task embeddings
    to a vector store for semantic search capabilities.
    """
    
    @abstractmethod
    def add(self, task_id: int, title: str, user_id: int) -> None:
        """
        Add a task embedding to the vector store.
        
        Args:
            task_id: ID of the task
            title: Title of the task for embedding
            user_id: ID of the user who owns the task
        """
        pass

class SearchableVectorStore(ABC):
    """
    Abstract base class for vector stores that support searching embeddings.
    
    This interface defines the contract for searching task embeddings
    in a vector store using semantic similarity.
    """
    
    @abstractmethod
    def search(self, query: str, user_id: int, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for similar tasks using semantic similarity.
        
        Args:
            query: Search query string
            user_id: ID of the user whose tasks to search
            top_k: Maximum number of results to return
            
        Returns:
            List of search results with task information
        """
        pass

class RemovableVectorStore(ABC):
    """
    Abstract base class for vector stores that support removing embeddings.
    
    This interface defines the contract for removing task embeddings
    from a vector store when tasks are deleted.
    """
    
    @abstractmethod
    def remove(self, task_id: int, user_id: int) -> None:
        """
        Remove a task embedding from the vector store.
        
        Args:
            task_id: ID of the task to remove
            user_id: ID of the user who owns the task
        """
        pass
