from backend.request.user_request import UserRequest
from utils.logger import logger
class DeleteTaskUserRequest(UserRequest):
    def __init__(self, user_id, task_id=None, task_title=None):
        super().__init__(user_id)
        self.task_id = task_id
        self.task_title = task_title

    @classmethod
    def create(cls, user_id, genai_client, user_input):
        max_attempts = 3
        attempt = 0
        task_id = None 
        task_title = None

        while attempt < max_attempts and not (task_id or task_title):
            data = genai_client.extract_task_id_or_title(user_input)
            task_id = data.get("task_id")
            task_title = data.get("task_title")
            logger.debug(f"DeleteTask create → task_id={task_id}, task_title={task_title}")
            
            if not (task_id or task_title):
                user_input =  input("I couldn't identify which task to delete. Please rephrase or provide the task title or ID: ")

            attempt += 1

        if not (task_id or task_title):
            raise Exception("Failed to identify the task to delete after multiple attempts. Please try again later.")        

        return DeleteTaskUserRequest(user_id, task_id, task_title)

    async def handle(self, task_service):
        task = None

        if self.task_id:
            logger.debug(f"Deleting task by ID: {self.task_id}")
            task = await task_service.get_task_by_id(self.task_id)

        elif self.task_title:
            logger.debug(f"Searching for task by title: {self.task_title}")
            tasks = await task_service.get_tasks(user_id=self.user_id)
            matching_tasks = [
                t for t in tasks
                if t["title"].strip().lower() == self.task_title.strip().lower()
            ] # TODO: use gemini embedding model and qdrant to search for the task
            if matching_tasks:
                task = matching_tasks[0]

        if task:
            await task_service.delete_task(task["id"])
            logger.info(f"Task '{task['title']}' deleted!")
        else:
            logger.info("Task not found.")
