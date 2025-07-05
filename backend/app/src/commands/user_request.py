"""
Base user request module for handling user commands.

This module defines the base UserRequest class that all specific
user request types inherit from.
"""

from typing import Protocol

class UserRequest:
    """
    Base class for all user request types.
    
    This class provides a common interface for all user request handlers.
    It stores the user ID and provides a foundation for request processing.
    
    Attributes:
        user_id: The ID of the user making the request
    """
    
    def __init__(self, user_id: int) -> None:
        self.user_id: int = user_id
