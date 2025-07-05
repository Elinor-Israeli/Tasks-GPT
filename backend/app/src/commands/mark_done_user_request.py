from typing import Optional, Dict, Any, List
from src.commands.user_request import UserRequest
from src.communicator import Communicator
from src.genai import AICommandInterpreter
from src.http_services.task_http_service import TaskHttpService
from src.vector_store.interfaces import SearchableVectorStore
from src.utils.logger import logger

class MarkDoneUserRequest(UserRequest):
    def __init__(self, user_id: int, task_id: Optional[int], communicator: Communicator) -> None:
        super().__init__(user_id)
        self.task_id: Optional[int] = task_id 
        self.communicator: Communicator = communicator

    @classmethod
    async def create(cls, user_id: int, genai_client: AICommandInterpreter, user_input: str, vector_searcher: SearchableVectorStore, communicator: Communicator) -> Optional['MarkDoneUserRequest']:
        data: Dict[str, Any] = genai_client.extract_task_id_or_title(user_input)

        task_id: Optional[int] = data.get("task_id")
        task_title: Optional[str] = data.get("task_title")
        logger.debug(f"MarkDone create → task_id={task_id}, task_title={task_title}")

        if not task_title and not task_id:
            task_title = (await communicator.input("What task would you like to mark as done? ")).strip()

        if not task_id and task_title:
            results: List[Dict[str, Any]] = vector_searcher.search(query=task_title, user_id=user_id, top_k=3)
            if results:
                await communicator.output("\nDid you mean one of these tasks?")
                for i, res in enumerate(results, start=1):
                    payload: Dict[str, Any] = res.payload
                    await communicator.output(f"{i}. {payload['title']} (task_id={payload['task_id']})")

                choice: str = (await communicator.input("Enter the task number to mark as done or 0 to cancel: ")).strip()
                if choice.isdigit() and 1 <= int(choice) <= len(results):
                    task_id = results[int(choice) - 1].payload["task_id"]
                else:
                    await communicator.output("Canceled or invalid choice.")
                    return None

        return MarkDoneUserRequest(user_id, task_id, communicator)
    
    async def handle(self, task_service: TaskHttpService, *args) -> None:
        logger.debug(f"Marking task by ID: {self.task_id}")
        task: Optional[Dict[str, Any]] = await task_service.get_task_by_id(self.task_id)

        if task:
            await task_service.update_task(task["id"], {"done": True})
            await self.communicator.output(f"Task '{task['title']}' marked as done!")
        else:
            logger.error("Task not found.")