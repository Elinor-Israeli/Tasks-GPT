from commands.user_request import UserRequest
from utils.logger import logger
from vector_store.interfaces import SearchableVectorStore
from genai import AICommandInterpreter
from http_services.task_http_service import TaskHttpService

class MarkDoneUserRequest(UserRequest):
    def __init__(self, user_id, task_id):
        super().__init__(user_id)
        self.task_id = task_id 

    @classmethod
    def create(cls, user_id: int, genai_client: AICommandInterpreter, user_input: str, vector_searcher: SearchableVectorStore):
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

        return MarkDoneUserRequest(user_id, task_id)
    
    async def handle(self, task_service: TaskHttpService, *args):
        logger.debug(f"Marking task by ID: {self.task_id}")
        task = await task_service.get_task_by_id(self.task_id)

        if task:
            await task_service.update_task(task["id"], {"done": True})
            logger.info(f"Task '{task['title']}' marked as done!")
        else:
            logger.error("Task not found.")