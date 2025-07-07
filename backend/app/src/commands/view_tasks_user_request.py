"""
View tasks user request module for handling task viewing commands.

This module contains the ViewTasksUserRequest class which handles
displaying tasks to users with various filtering options.
"""

from typing import Optional, Dict, Any, List
from src.commands.user_request import UserRequest
from src.communicator import Communicator
from src.genai import AICommandInterpreter
from src.http_services.task_http_service import TaskHttpService
from src.utils.logger import logger
from src.vector_store.interfaces import SearchableVectorStore, EditableVectorStore
from src.utils.menus import view_options, ViewOption

class ViewTasksUserRequest(UserRequest):
    """
    User request handler for viewing tasks.
    
    This class handles displaying tasks to users with various
    filtering options including completion status and due dates.
    
    Attributes:
        choice: User's view choice (1-5 for different filter options)
    """
    
    def __init__(self, user_id: int, choice: str) -> None:
        """
        Initialize a view tasks request.
        
        Args:
            user_id: The ID of the user viewing tasks
            choice: The user's view choice (1-5)
        """
        super().__init__(user_id)
        self.choice: str = choice
    
    @classmethod
    async def create(cls, user_id: int, genai_client: AICommandInterpreter, user_input: str, vector_searcher: SearchableVectorStore, communicator: Communicator) -> Optional['ViewTasksUserRequest']:
        """
        Create a ViewTasksUserRequest instance from user input.
        
        This method uses AI to interpret the user's view request and
        prompts for clarification if needed.
        
        Args:
            user_id: The ID of the user viewing tasks
            genai_client: AI client for interpreting view commands
            user_input: Natural language input describing what to view
            vector_searcher: Vector store for semantic search
            communicator: Communication interface for user interaction
            
        Returns:
            ViewTasksUserRequest instance if successful, None if cancelled
        """
        result: Dict[str, Any] = genai_client.interpret_view_task_command(user_input, view_options)
        if result["status"] == "error":
            await communicator.output(result["message"])
            return None
    
        await communicator.output(result["message"])

        if result["status"] == "specific" and result["choice"] in {"1", "2", "3", "4", "5"}:
            return ViewTasksUserRequest(user_id, result["choice"], communicator)
        
        follow_up_input: str = await communicator.input("")
        follow_up_result: Dict[str, Any] = genai_client.interpret_view_task_command(follow_up_input, view_options)

        if follow_up_result["status"] == "specific" and follow_up_result["choice"] in {"1", "2", "3", "4", "5"}:
            return ViewTasksUserRequest(user_id, follow_up_result["choice"], communicator)

        return ViewTasksUserRequest(user_id, follow_up_result["choice"])

    async def handle(self, task_service: TaskHttpService, vector_editor: EditableVectorStore, communicator: Communicator) -> None:
        """
        Execute the view tasks request.
        
        This method retrieves tasks based on the user's choice and
        displays them in a formatted list.
        
        Args:
            task_service: Service for task-related operations
            *args: Additional arguments (unused)
        """

        filter_kwargs: Dict[str, Any] = {
            '1': {'done': True},
            '2': {'done': False},
            '3': {'overdue': True},
            '4': {'upcoming': True},
            '5': {},
        }.get(self.choice, {})

        tasks: List[Dict[str, Any]] = await task_service.get_tasks(user_id=self.user_id, **filter_kwargs)
        
        if not tasks:
            await communicator.output("No tasks found for this option.")
            return

        tasks = sorted(tasks, key=lambda x: x['id'], reverse=True)

        await communicator.output("\n--- TASKS ---")
        for task in tasks:
            status: str = "✅" if task['done'] else "❌"
            due: str = f"(Due: {task['due_date']})" if task["due_date"] else ""
            await communicator.output(f"{task['id']}. {task['title']} {due} - {status}")
