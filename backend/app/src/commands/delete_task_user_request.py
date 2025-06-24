from src.commands.user_request import UserRequest
from src.communicator import Communicator
from src.genai import AICommandInterpreter
from src.http_services.task_http_service import TaskHttpService
from src.vector_store.interfaces import SearchableVectorStore, RemovableVectorStore
from src.utils.logger import logger

class DeleteTaskUserRequest(UserRequest):
    def __init__(self, user_id, task_id, task_title, communicator: Communicator ):
        super().__init__(user_id)
        self.task_id = task_id
        self.task_title = task_title
        self.communicator = communicator

    @classmethod
    async def create(cls, user_id:int, genai_client:AICommandInterpreter, user_input: str, vector_searcher: SearchableVectorStore, communicator: Communicator):
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
                user_input = communicator.input("What task would you like to delete?  ")

            attempt += 1

        if not task_id and task_title:
            results = vector_searcher.search(query=task_title, user_id=user_id, top_k=3)
            if results:
                communicator.output("\nDid you mean one of these tasks?")
                for i, res in enumerate(results, start=1):
                    payload = res.payload
                    communicator.output(f"{i}. {payload['title']} (task_id={payload['task_id']})")

                choice = (await communicator.input("Enter the task number to delete or 0 to cancel: ")).strip()
                if choice.isdigit() and 1 <= int(choice) <= len(results):
                    task_id = results[int(choice) - 1].payload["task_id"]
                else:
                    raise Exception("Canceled or invalid choice.")

        if not (task_id or task_title):
            raise Exception("Failed to identify the task to delete after multiple attempts. Please try again later.")        

        return DeleteTaskUserRequest(user_id, task_id, task_title, communicator)

    async def handle(self, task_service: TaskHttpService, vector_remover: RemovableVectorStore):
        
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
            ]
            if matching_tasks:
                task = matching_tasks[0]

        if task:
            await task_service.delete_task(task["id"])
            await self.communicator.output(f"Task '{task['title']}' deleted!")

            vector_remover.remove(task_id=task["id"], user_id=self.user_id)
            logger.debug(f"Removed task {task['id']} from vector store.")
        else:
            await self.communicator.output("Task not found.")
