import random
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
            logger.info("Hmm... I couldn’t find a task with that ID. Want to try again?")
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
            await communicator.output("I didn’t quite catch that. Let’s try again manually:")
            title = (await communicator.input("New title? (or leave blank): ")).strip()
            due_date = (await communicator.input("New due date? (YYYY-MM-DD or leave blank): ")).strip()
            extracted = {
                "title": title if title else None,
                "due_date": due_date if due_date else None
            }     

        return EditTaskUserRequest(user_id, task_id, extracted, communicator)


    async def handle(self, task_service: TaskHttpService, vector_store: TaskVectorStore, communicator: Communicator):
        data = {}
        payload_update = {}

        title = self.extracted_data.get("title")
        if title:
            data["title"] = title
            payload_update["title"] = title
            await communicator.output(f"Okay, updating the title to: '{title}' ✏️")

        due_date = self.extracted_data.get("due_date")
        if due_date:
            try:
                datetime.strptime(due_date, "%Y-%m-%d")
                data["due_date"] = due_date
                payload_update["due_date"] = due_date
                await communicator.output(f"Setting the new due date to: {due_date} 📆")
            except ValueError:
                await communicator.output("Oops! That date format looks off. Use YYYY-MM-DD format please 🙏")
                return

        if not data:
            await communicator.output("Hmm, I didn’t get any changes to apply. Want to try again?")
            return

        await task_service.update_task(int(self.task_id), data)
        vector_store.add(
            task_id=int(self.task_id),
            title=payload_update.get("title") or title,
            user_id=self.user_id,
            due_date=payload_update.get("due_date")
        )

        confirmations = [
            "All done! ✨ Your task is updated.",
            "✅ Changes saved! You're all set.",
            "Task updated successfully! Want to do anything else?",
            f"Great — I've updated '{title or 'your task'}'. Let me know what’s next!"
        ]
        await communicator.output(random.choice(confirmations))