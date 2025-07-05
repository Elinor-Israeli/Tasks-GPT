"""
Add task user request module for handling task creation commands.

This module contains the AddTaskUserRequest class which handles the
creation of new tasks with AI-powered data extraction.
"""

from datetime import datetime
from typing import Optional, Dict, Any

import httpx

from src.communicator import Communicator
from src.genai import AICommandInterpreter
from src.http_services.task_http_service import TaskHttpService
from src.utils.logger import logger
from src.vector_store.interfaces import AddableVectorStore
from .user_request import UserRequest

class AddTaskUserRequest(UserRequest):
    """
    User request handler for adding new tasks.
    
    This class handles the creation of new tasks with AI-powered
    extraction of task title and due date from natural language input.
    
    Attributes:
        title: The title of the task to create
        due_date: The due date for the task (YYYY-MM-DD format)
        communicator: Communication interface for user interaction
    """
    
    def __init__(self, user_id: int, title: str, due_date: str, communicator: Communicator) -> None:
        super().__init__(user_id)
        self.title: str = title  
        self.due_date: str = due_date
        self.communicator: Communicator = communicator

    @classmethod
    async def create(cls, user_id: int, genai_client: AICommandInterpreter, user_input: str, communicator: Communicator) -> Optional['AddTaskUserRequest']:
        """
        Create an AddTaskUserRequest instance from user input.
        
        This method uses AI to extract task information from natural language
        and prompts the user for missing information if needed.
        
        Args:
            user_id: The ID of the user creating the task
            genai_client: AI client for extracting task data
            user_input: Natural language input describing the task
            communicator: Communication interface for user interaction
            
        Returns:
            AddTaskUserRequest instance if successful, None if cancelled
        """
        logger.info(f"Extract task data with user_input: {user_input}")
        extraction: Dict[str, Any] = genai_client.extract_task_data(user_input)
        title: Optional[str] = extraction.get("name")
        due_date: Optional[str] = extraction.get("date")

        logger.debug(f"AI extracted: title={title}, date={due_date}")

        while not title or title.lower() == "none":
            user_input = (await communicator.input("Great! enter your task title and due date : ")).strip()
            extraction = genai_client.extract_task_data(user_input)
            title = extraction.get("name")
            due_date = extraction.get("date")
            logger.debug(f"Re-extracted: title={title}, date={due_date}")

        while not due_date or due_date.lower() == "none":
            user_input = (await communicator.input("Enter due date or include it in a full sentence (e.g., 'Walk dog next week'): ")).strip()
            extraction = genai_client.extract_task_data(user_input)
            if not title and extraction.get("name"):
                title = extraction.get("name")
            due_date = extraction.get("date")
            logger.debug(f"Re-extracted: title={title}, date={due_date}")

        try:
            parsed_date: datetime = datetime.strptime(due_date, "%Y-%m-%d")
            due_date = parsed_date.strftime("%Y-%m-%d")
        except ValueError:
            logger.info("Invalid date format. Please use YYYY-MM-DD. Task not added.")
            return None

        return AddTaskUserRequest(user_id, title, due_date, communicator)

    async def handle(self, task_service: TaskHttpService, vector_adder: AddableVectorStore, communicator: Communicator) -> None:
        """
        Execute the add task request.
        
        This method creates the task in the database and adds it to
        the vector store for semantic search capabilities.
        
        Args:
            task_service: Service for task-related operations
            vector_adder: Vector store for adding task embeddings
            communicator: Communication interface for user interaction
        """
        self.communicator = communicator

        try:
            task: Dict[str, Any] = await task_service.create_task({
                "title": self.title,
                "due_date": self.due_date,
                "user_id": self.user_id
            })

            vector_adder.add(
                task_id=task["id"],
                title=self.title,
                user_id=self.user_id
            )

            await communicator.output(f"Task '{self.title}' added with due date {self.due_date}!")

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 400:
                error_detail: str = e.response.json().get("detail", "Unknown error")

                if "already exists" in error_detail.lower():
                    raise ValueError("A task with this title already exists.")

                logger.error(f"Failed to add task: {error_detail}")
            else:
                logger.error(f"Unexpected error while adding task: {e}")
