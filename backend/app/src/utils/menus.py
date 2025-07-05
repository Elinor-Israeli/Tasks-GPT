"""
Menu utilities module for the TaskGPT application.

This module provides menu choice enums and view options for
the application's user interface.
"""

from enum import Enum
from typing import Final

class MenuChoice(str, Enum):
    """
    Enumeration of available menu choices for user interactions.
    
    This enum defines the different actions a user can perform
    in the TaskGPT application.
    """
    VIEW_TASKS = "1"
    ADD_TASK = "2"
    MARK_DONE = "3"
    DELETE_TASK = "4"
    EDIT_TASK = "5"
    NONE = "None"

# Predefined view options for task filtering
view_options: Final[str] = """
    1. Completed Tasks
    2. Incomplete Tasks
    3. Overdue Tasks
    4. Upcoming Tasks
    5. All Tasks
    """    

class ViewOption(str, Enum):
    """
    Enumeration of available view options for task filtering.
    
    This enum defines the different ways users can view their tasks
    based on completion status and due dates.
    """
    COMPLETED_TASKS = '1'
    INCOMPLETE_TASKS = '2'
    OVERDUE_TASKS = '3'
    UPCOMING_TASKS ='4'
    ALL_TASKS = '5'