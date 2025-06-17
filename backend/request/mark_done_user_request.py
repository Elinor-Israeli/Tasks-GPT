from backend.request.user_request import UserRequest
from utils.logger import logger
from vector_store.interfaces import Searchable
class MarkDoneUserRequest(UserRequest):
    def __init__(self, user_id, task_id, task_title, vector_searcher: Searchable):
        super().__init__(user_id)
        self.task_id = task_id 
        self.task_title = task_title 
        self.vector_searcher = vector_searcher

    @classmethod
    def create(cls, user_id, genai_client, user_input, vector_searcher):
        data = genai_client.extract_task_id_or_title(user_input)

        task_id = data.get("task_id")
        task_title = data.get("task_title")
        logger.debug(f"MarkDone create → task_id={task_id}, task_title={task_title}")

        if not task_title and not task_id:
            task_title = input("What task would you like to mark as done? ").strip()

        if not task_id and task_title:
            results = vector_searcher.search(query=task_title, user_id=user_id, top_k=3)
            if results:
                print("\nDid you mean one of these tasks?")
                for i, res in enumerate(results, start=1):
                    payload = res.payload
                    print(f"{i}. {payload['title']} (task_id={payload['task_id']})")

                choice = input("Enter the task number to mark as done or 0 to cancel: ").strip()
                if choice.isdigit() and 1 <= int(choice) <= len(results):
                    task_id = results[int(choice) - 1].payload["task_id"]
                else:
                    print("Canceled or invalid choice.")
                    return None

        return MarkDoneUserRequest(user_id, task_id, task_title, vector_searcher)
    
    async def handle(self, task_service):
        task = None

        if self.task_id:
            logger.debug(f"Marking task by ID: {self.task_id}")
            task = await task_service.get_task_by_id(self.task_id)

        elif self.task_title:
            logger.debug(f"Searching for task by title: {self.task_title}")
            tasks = await task_service.get_tasks(user_id=self.user_id)
            matching_tasks = [
                t for t in tasks
                if t["title"].strip().lower() == self.task_title.strip().lower()
            ]
            if matching_tasks:
                task = matching_tasks[0]

        else:
            logger.error("Could not identify task from input.")
            return

        if task:
            await task_service.update_task(task["id"], {"done": True})
            logger.info(f"Task '{task['title']}' marked as done!")
        else:
            logger.error("Task not found.")