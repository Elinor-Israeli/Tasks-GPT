from datetime import datetime
from backend.request.user_request import UserRequest
from utils.logger import logger
from vector_store.interfaces import Searchable
class EditTaskUserRequest(UserRequest):
    def __init__(self, user_id, task_id,extracted_data, vector_searcher: Searchable):
        super().__init__(user_id)
        self.task_id = task_id
        self.extracted_data = extracted_data
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

        task_title = task.get('title', 'this task')
        user_input = input(f"Great! You want to edit '{task_title}'. Enter your changes: ").strip()
        extracted = genai_client.extract_edit_task_data(user_input)
        logger.debug(f"Extracted update data: {extracted}")
        return EditTaskUserRequest(user_id, task_id, extracted, vector_searcher)


    async def handle(self, task_service):
        data = {}
        title = self.extracted_data.get("title")
        if title:
            data["title"] = title

        due_date = self.extracted_data.get("due_date")
        if due_date:
            try:
                datetime.strptime(due_date, "%Y-%m-%d")
                data["due_date"] = due_date
            except ValueError:
                logger.info("Invalid date format. Please use YYYY-MM-DD.")
                return

        if not data:
            logger.info("No valid update data found.")
            return

        await task_service.update_task(int(self.task_id), data)
        logger.info("Task updated!")