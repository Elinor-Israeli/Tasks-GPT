from datetime import datetime
from backend.request.user_request import UserRequest
from utils.logger import logger
from vector_store.interfaces import Searchable
from qdrant_client.http.models import Filter, FieldCondition, MatchValue
class EditTaskUserRequest(UserRequest):
    def __init__(self, user_id, task_id, choice, vector_searcher: Searchable):
        super().__init__(user_id)
        self.task_id = task_id
        self.choice = choice
        self.vector_searcher = vector_searcher

    @classmethod
    async def create(cls, user_id, task_service, genai_client, user_input, vector_searcher:Searchable):
        data = genai_client.extract_task_id_or_title_to_edit(user_input)
        task_id = data.get("task_id")
        task_title = data.get("task_title")

        logger.debug(f"AI extracted task_id={task_id}, task_title={task_title}")

        if not task_title and not task_id:
            task_title = input("What task would you like to edit?\n").strip()

        if not task_id and task_title:
            results = vector_searcher.search(query=task_title, user_id=user_id, top_k=3)
            if results:
                print("\nDid you mean one of these tasks?")
                for i, res in enumerate(results, start=1):
                    payload = res.payload
                    print(f"{i}. {payload['title']} (task_id={payload['task_id']})")

                choice = input("Enter the task number to edit or 0 to cancel: ").strip()
                if choice.isdigit() and 1 <= int(choice) <= len(results):
                    task_id = results[int(choice) - 1].payload["task_id"]
                else:
                    print("Canceled or invalid choice.")
                    return None

        if not task_id:
            task_id = input("Enter task ID to edit: ").strip()

        task = await task_service.get_task_by_id(task_id)
        if not task:
            logger.info("Task not found.")
            return None

        logger.info(f"\nEditing Task {task['id']} - {task['title']}")

        edit_options = """
        1. Title
        2. Due Date
        3. Both
        4. Cancel
        """

        edit_types = genai_client.interpret_edit_task_command(user_input, edit_options)
        if not edit_types or edit_types.lower() == "none":
            choice = input("What would you like to edit?\n" + edit_options + "\n").strip()
        else:
            choice = edit_types

        return EditTaskUserRequest(user_id, task_id, choice, vector_searcher)


    async def handle(self, task_service):
        data = {}

        if self.choice == "1":
            data["title"] = input("Enter new title: ")
        elif self.choice == "2":
            new_due_date = input("Enter new due date (YYYY-MM-DD): ")
            try:
                datetime.strptime(new_due_date, "%Y-%m-%d")
                data["due_date"] = new_due_date
            except ValueError:
                logger.info("Invalid date format. Please use YYYY-MM-DD.")
                return
        elif self.choice == "3":
            data["title"] = input("Enter new title: ")
            new_due_date = input("Enter new due date (YYYY-MM-DD): ")
            try:
                datetime.strptime(new_due_date, "%Y-%m-%d")
                data["due_date"] = new_due_date
            except ValueError:
                logger.info("Invalid date format. Please use YYYY-MM-DD.")
                return
        else:
            logger.info("Edit cancelled.")
            return

        await task_service.update_task(int(self.task_id), data)
        logger.info("Task updated!")
