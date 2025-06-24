from datetime import datetime
from typing import Dict, Optional

from src.commands.user_request import UserRequest
from src.communicator import Communicator
from src.genai import AICommandInterpreter
from src.http_services.task_http_service import TaskHttpService
from src.vector_store.interfaces import SearchableVectorStore
from src.vector_store.task_vector_store import TaskVectorStore
from src.utils.logger import logger


class EditTaskUserRequest(UserRequest):
    def __init__(self, user_id: int, task_id: int,extracted_data: Dict[str, Optional[str]], communicator: Communicator):
        super().__init__(user_id)
        self.task_id = task_id
        self.extracted_data = extracted_data
        self.communicator = communicator

    @classmethod
    async def create(
        cls, 
        user_id: int, 
        task_service: TaskHttpService, 
        genai_client: AICommandInterpreter, 
        user_input: str, 
        vector_searcher:SearchableVectorStore, 
        communicator: Communicator
    ):
        data = genai_client.extract_task_id_or_title_to_edit(user_input)
        task_id = data.get("task_id")
        task_title = data.get("task_title")
        
        logger.debug(f"AI extracted task_id={task_id}, task_title={task_title}")

        if not task_title and not task_id:
            task_title = (await communicator.input("What task would you like to edit?\n")).strip()

        if not task_id and task_title:
            results = vector_searcher.search(query=task_title, user_id=user_id, top_k=3)
            if results:
                await communicator.output("\nDid you mean one of these tasks?")
                for i, res in enumerate(results, start=1):
                    payload = res.payload
                    await communicator.output(f"{i}. {payload['title']} (task_id={payload['task_id']})")

                choice = (await communicator.input("Enter the task number to edit or 0 to cancel: ")).strip()
                if choice.isdigit() and 1 <= int(choice) <= len(results):
                    task_id = results[int(choice) - 1].payload["task_id"]
                else:
                    await communicator.output("Canceled or invalid choice.")
                    return None

        if not task_id:
            task_id = await (communicator.input("Enter task ID to edit: ")).strip()

        task = await task_service.get_task_by_id(task_id)
        if not task:
            logger.info("Task not found.")
            return None

        await communicator.output(f"\nEditing Task {task['id']} - {task['title']}")

        task_title = task.get('title', 'this task')
        user_input = (await communicator.input(f"Great! You want to edit '{task_title}'. Enter your changes: ")).strip()

        try:
            extracted = genai_client.extract_edit_task_data(user_input)
            logger.debug(f"Extracted update data: {extracted}")
        except Exception as e:
            logger.error(f"Failed to extract edit task data: {e}")
            extracted = {"title": None, "due_date": None} 

        if not extracted.get("title") and not extracted.get("due_date"):
            await communicator.output("Sorry, I couldn't understand your changes.")
            title = (await communicator.input("Enter the new title (or press Enter to skip): ")).strip()
            due_date = (await communicator.input("Enter new due date (YYYY-MM-DD) or press Enter to skip: ")).strip()
            extracted = {
                "title": title if title else None,
                "due_date": due_date if due_date else None
            }     

        return EditTaskUserRequest(user_id, task_id, extracted, communicator)


    async def handle(self, task_service: TaskHttpService, vector_store: TaskVectorStore, communicator: Communicator):
        
        data = {}
        title = self.extracted_data.get("title")
        if title:
            data["title"] = title
            vector_store.add(
            task_id=int(self.task_id),
            title=title,
            user_id=self.user_id
            )

        due_date = self.extracted_data.get("due_date")
        if due_date:
            try:
                datetime.strptime(due_date, "%Y-%m-%d")
                data["due_date"] = due_date
            except ValueError:
                await self.communicator.output("Invalid date format. Please use YYYY-MM-DD.")
                return

        if not data:
            await self.communicator.output("No valid update data found.")
            return

        await task_service.update_task(int(self.task_id), data)
        await self.communicator.output("Task updated!")