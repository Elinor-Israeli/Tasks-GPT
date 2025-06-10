from backend.request.user_request import UserRequest
from utils.logger import logger

class MarkDoneUserRequest(UserRequest):
    def __init__(self, user_id, task_id=None, task_title=None):
        super().__init__(user_id)
        self.task_id = task_id 
        self.task_title = task_title 

    @classmethod
    def create(cls, user_id, genai_client, user_input):
        data = genai_client.extract_task_id_or_title(user_input)

        task_id = data.get("task_id")
        task_title = data.get("task_title")
        logger.debug(f"MarkDone create → task_id={task_id}, task_title={task_title}")

        return MarkDoneUserRequest(user_id, task_id, task_title)
    
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