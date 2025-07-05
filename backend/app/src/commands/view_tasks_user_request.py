from typing import Optional, Dict, Any, List
from src.commands.user_request import UserRequest
from src.communicator import Communicator
from src.genai import AICommandInterpreter
from src.http_services.task_http_service import TaskHttpService
from src.utils.logger import logger
from src.vector_store.interfaces import SearchableVectorStore
from src.utils.menus import view_options, ViewOption

class ViewTasksUserRequest(UserRequest):
    def __init__(self, user_id: int, choice: str, communicator: Communicator) -> None:
        super().__init__(user_id)
        self.choice: str = choice
        self.communicator: Communicator = communicator
    
    @classmethod
    async def create(cls, user_id: int, genai_client: AICommandInterpreter, user_input: str, vector_searcher: SearchableVectorStore, communicator: Communicator) -> Optional['ViewTasksUserRequest']:
        result: Dict[str, Any] = genai_client.interpret_view_task_command(user_input, view_options)
        if result["status"] == "error":
            await communicator.output(result["message"])
            return None
    
        await communicator.output(result["message"])

        if result["status"] == "specific" and result["choice"] in {"1", "2", "3", "4", "5"}:
            return ViewTasksUserRequest(user_id, result["choice"], communicator)
        
        follow_up_input: str = await communicator.input("")
        follow_up_result: Dict[str, Any] = genai_client.interpret_view_task_command(follow_up_input, view_options)

        if follow_up_result["status"] == "specific" and follow_up_result["choice"] in {"1", "2", "3", "4", "5"}:
            return ViewTasksUserRequest(user_id, follow_up_result["choice"], communicator)

        return ViewTasksUserRequest(user_id, follow_up_result["choice"], communicator)

    async def handle(self, task_service: TaskHttpService, *args) -> None:
        comm: Communicator = self.communicator

        filter_kwargs: Dict[str, Any] = {
            '1': {'done': True},
            '2': {'done': False},
            '3': {'overdue': True},
            '4': {'upcoming': True},
            '5': {},
        }.get(self.choice, {})

        tasks: List[Dict[str, Any]] = await task_service.get_tasks(user_id=self.user_id, **filter_kwargs)
        
        if not tasks:
            await comm.output("No tasks found for this option.")
            return

        tasks = sorted(tasks, key=lambda x: x['id'], reverse=True)

        await comm.output("\n--- TASKS ---")
        for task in tasks:
            status: str = "✅" if task['done'] else "❌"
            due: str = f"(Due: {task['due_date']})" if task["due_date"] else ""
            await comm.output(f"{task['id']}. {task['title']} {due} - {status}")
