"""
Delete task user request module for handling task deletion commands.

This module contains the DeleteTaskUserRequest class which handles
the deletion of tasks with AI-powered task identification.
"""

from typing import Optional, Dict, Any, List
from src.commands.user_request import UserRequest
from src.communicator import Communicator
from src.genai import AICommandInterpreter
from src.http_services.task_http_service import TaskHttpService
from src.vector_store.interfaces import SearchableVectorStore, EditableVectorStore
from src.utils.logger import logger

class DeleteTaskUserRequest(UserRequest):
    """
    User request handler for deleting tasks.
    
    This class handles the deletion of tasks with AI-powered
    identification of tasks by title or ID.
    
    Attributes:
        task_id: ID of the task to delete (if known)
        task_title: Title of the task to delete (if known)
    """
    
    def __init__(self, user_id: int, task_id: Optional[int], task_title: Optional[str]) -> None:
        super().__init__(user_id)
        self.task_id: Optional[int] = task_id
        self.task_title: Optional[str] = task_title

    @classmethod
    async def create(cls, user_id: int, genai_client: AICommandInterpreter, user_input: str, vector_searcher: SearchableVectorStore, communicator: Communicator) -> Optional['DeleteTaskUserRequest']:
        """
        Create a DeleteTaskUserRequest instance from user input.
        
        This method uses AI to extract task information from natural language
        and provides task selection options if needed.
        
        Args:
            user_id: The ID of the user deleting the task
            genai_client: AI client for extracting task data
            user_input: Natural language input describing the task to delete
            vector_searcher: Vector store for semantic search
            communicator: Communication interface for user interaction
            
        Returns:
            DeleteTaskUserRequest instance if successful, None if cancelled
        """
    
        data: Dict[str, Any] = genai_client.extract_task_id_or_title(user_input)
        task_id: Optional[int] = data.get("task_id")
        task_title: Optional[str] = data.get("task_title")

        logger.debug(f"DeleteTask create → task_id={task_id}, task_title={task_title}")
        
        if not task_id and not task_title:
            task_title = (await communicator.input("What task would you like to delete?\n")).strip()

        if not task_id and task_title:
            results: List[Dict[str, Any]] = vector_searcher.search(query=task_title, user_id=user_id, top_k=3)
            if results:
                await communicator.output("\nDid you mean one of these tasks?")
                for i, res in enumerate(results, start=1):
                    payload: Dict[str, Any] = res.payload
                    await communicator.output(f"{i}. {payload['title']} (task_id={payload['task_id']})")

                choice: str = (await communicator.input("Enter the task number to delete or 0 to cancel: ")).strip()
                if choice.isdigit() and 1 <= int(choice) <= len(results):
                    task_id = results[int(choice) - 1].payload["task_id"]
                else:
                    raise Exception("Canceled or invalid choice.")

        if not (task_id or task_title):
            raise Exception("Failed to identify the task to delete after multiple attempts. Please try again later.")        

        return DeleteTaskUserRequest(user_id, task_id, task_title)

    async def handle(self, task_service: TaskHttpService, vector_editor: EditableVectorStore, communicator: Communicator) -> bool:
        """
        Execute the delete task request.
        
        This method deletes the task from the database and removes
        its embedding from the vector store.
        
        Args:
            task_service: Service for task-related operations
            vector_editor: Vector store for removing task embeddings
            *args: Additional arguments (unused)
            
        Returns:
        bool: True if task was successfully added, False otherwise.    
        """
        
        task: Optional[Dict[str, Any]] = None

        if self.task_id:
            logger.debug(f"Deleting task by ID: {self.task_id}")
            task = await task_service.get_task_by_id(self.task_id)

        elif self.task_title:
            logger.debug(f"Searching for task by title: {self.task_title}")
            tasks: List[Dict[str, Any]] = await task_service.get_tasks(user_id=self.user_id)
            matching_tasks: List[Dict[str, Any]] = [
                t for t in tasks
                if t["title"].strip().lower() == self.task_title.strip().lower()
            ]
            if matching_tasks:
                task = matching_tasks[0]

        if task:
            await task_service.delete_task(task["id"])
            await communicator.output(f"Task '{task['title']}' deleted!")

            vector_editor.remove(task_id=task["id"], user_id=self.user_id)
            logger.debug(f"Removed task {task['id']} from vector store.")
            return True
        else:
            await communicator.output("Task not found.")
            return False
