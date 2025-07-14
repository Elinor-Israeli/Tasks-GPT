"""
Edit task user request module for handling task editing commands.

This module contains the EditTaskUserRequest class which handles
editing tasks with AI-powered data extraction and validation.
"""

import random
from datetime import datetime
from typing import Dict, Optional, Any

from src.commands.user_request import UserRequest
from src.communicator import Communicator
from src.genai import AICommandInterpreter
from src.http_services.task_http_service import TaskHttpService
from src.vector_store.interfaces import SearchableVectorStore, EditableVectorStore
from src.utils.logger import logger

class EditTaskUserRequest(UserRequest):
    """
    User request handler for editing tasks.
    
    This class handles editing tasks with AI-powered extraction
    of task information and validation of changes.
    
    Attributes:
        task_id: ID of the task to edit
        extracted_data: Dictionary containing extracted edit data
    """
    
    def __init__(self, user_id: int, task_id: int, extracted_data: Dict[str, Optional[str]]) -> None:
        super().__init__(user_id)
        self.task_id: int = task_id
        self.extracted_data: Dict[str, Optional[str]] = extracted_data

    @classmethod
    async def create(
        cls, 
        user_id: int, 
        task_service: TaskHttpService, 
        genai_client: AICommandInterpreter, 
        user_input: str, 
        vector_searcher: SearchableVectorStore, 
        communicator: Communicator
    ) -> Optional['EditTaskUserRequest']:
        """
        Create an EditTaskUserRequest instance from user input.
        
        This method uses AI to extract task and edit information from natural language
        and prompts for clarification if needed.
        
        Args:
            user_id: The ID of the user editing the task
            task_service: Service for task-related operations
            genai_client: AI client for extracting task data
            user_input: Natural language input describing the task to edit
            vector_searcher: Vector store for semantic search
            communicator: Communication interface for user interaction
            
        Returns:
            EditTaskUserRequest instance if successful, None if cancelled
        """
        data: Dict[str, Any] = genai_client.extract_task_id_or_title_to_edit(user_input)
        task_id: Optional[int] = data.get("task_id")
        task_title: Optional[str] = data.get("task_title")
        
        logger.debug(f"AI extracted task_id={task_id}, task_title={task_title}")

        if not task_title and not task_id:
            task_title = (await communicator.input(" ")).strip()

        if not task_id and task_title:
            results = vector_searcher.search(query=task_title, user_id=user_id, top_k=3)
            if results:
                await communicator.output("\nDid you mean one of these?")
                for i, res in enumerate(results, start=1):
                    payload = res.payload
                    await communicator.output(f"{i}. {payload['title']} (task_id={payload['task_id']})")

                choice = (await communicator.input("Enter the task number to edit or 0 to cancel: ")).strip()
                if choice.isdigit() and 1 <= int(choice) <= len(results):
                    task_id = results[int(choice) - 1].payload["task_id"]
                else:
                    await communicator.output("Got it — canceling the edit for now.")
                    return None

        if not task_id:
            task_id = await (communicator.input("Could you share the task ID you'd like to edit? ")).strip()

        task = await task_service.get_task_by_id(task_id)
        if not task:
            logger.info("Hmm... I couldn't find a task with that ID. Want to try again?")
            return None

        await communicator.output(f"\nCool, we're editing: '{task['title']}' (ID: {task['id']})")        
        user_input = (await communicator.input(f"What would you like to change about '{task['title']}'?\n")).strip()

        try:
            extracted = genai_client.extract_edit_task_data(user_input)
            logger.debug(f"Extracted update data: {extracted}")
        except Exception as e:
            logger.error(f"Failed to extract edit task data: {e}")
            extracted = {"title": None, "due_date": None} 

        if not extracted.get("title") and not extracted.get("due_date"):
            await communicator.output("I didn't quite catch that. Let's try again manually:")
            title = (await communicator.input("New title? (or leave blank): ")).strip()
            due_date = (await communicator.input("New due date? (YYYY-MM-DD or leave blank): ")).strip()
            extracted = {
                "title": title if title else None,
                "due_date": due_date if due_date else None
            }     

        return EditTaskUserRequest(user_id, task_id, extracted)


    async def handle(self, task_service: TaskHttpService, vector_editor: EditableVectorStore, communicator: Communicator) -> bool:
        """
        Execute the edit task request.
        
        This method updates the task in the database and refreshes
        its embedding in the vector store.
        
        Args:
            task_service: Service for task-related operations
            vector_editor: Vector store for updating task embeddings
            communicator: Communication interface for user interaction

        Returns:
        bool: True if task was successfully added, False otherwise.    
        """
        data: Dict[str, Any] = {}
        payload_update: Dict[str, Optional[str]] = {}

        title: Optional[str] = self.extracted_data.get("title")
        if title:
            data["title"] = title
            payload_update["title"] = title
            await communicator.output(f"Okay, updating the title to: '{title}' ✏️")
            return True

        due_date: Optional[str] = self.extracted_data.get("due_date")
        if due_date:
            try:
                datetime.strptime(due_date, "%Y-%m-%d")
                data["due_date"] = due_date
                payload_update["due_date"] = due_date
                await communicator.output(f"Setting the new due date to: {due_date} 📆")
                return True
            except ValueError:
                await communicator.output("Oops! That date format looks off. Use YYYY-MM-DD format please 🙏")
                return False

        if not data:
            await communicator.output("Hmm, I didn't get any changes to apply. Want to try again?")
            return False

        await task_service.update_task(int(self.task_id), data)
        vector_editor.add(
            task_id=int(self.task_id),
            title=payload_update.get("title") or title,
            user_id=self.user_id,
            due_date=payload_update.get("due_date")
        )

        confirmations = [
            "All done! ✨ Your task is updated.",
            "✅ Changes saved! You're all set.",
            "Task updated successfully! Want to do anything else?",
            f"Great — I've updated '{title or 'your task'}'. Let me know what's next!"
        ]
        await communicator.output(random.choice(confirmations))