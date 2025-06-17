from backend.request.user_request import UserRequest
from client.menus import view_options
from utils.logger import logger
from client.genai import AICommandInterpreter
from client.http_services.task_http_service import TaskHttpService
class ViewTasksUserRequest(UserRequest):
    def __init__(self, user_id, choice):
        super().__init__(user_id)
        self.choice = choice

    @classmethod
    def create(cls, user_id, genai_client:AICommandInterpreter, user_input: str):
        view_types = genai_client.interpret_view_task_command(user_input, view_options)
        choice = view_types if view_types else input("Choose an option:\n" + view_options + "\n").strip()

        if not choice or choice not in {"1", "2", "3", "4", "5"}:
            logger.info("Invalid choice. Please try again.")
            return None

        return ViewTasksUserRequest(user_id, choice)

    async def handle(self, task_service: TaskHttpService, *args):
        if self.choice == "1":
            tasks = await task_service.get_tasks(user_id=self.user_id, done=True)
        elif self.choice == "2":
            tasks = await task_service.get_tasks(user_id=self.user_id, done=False)
        elif self.choice == "3":
            tasks = await task_service.get_tasks(user_id=self.user_id, overdue=True)
        elif self.choice == "4":
            tasks = await task_service.get_tasks(user_id=self.user_id, upcoming=True)
        elif self.choice == "5":
            tasks = await task_service.get_tasks(user_id=self.user_id)
        else:
            tasks = await task_service.get_tasks(user_id=self.user_id)

        if not tasks:
            logger.info("No tasks found for this option.")
            return

        tasks = sorted(tasks, key=lambda x: x['id'], reverse=True)

        print("\n--- TASKS ---")
        for task in tasks:
            status = "✅" if task['done'] else "❌"
            due = f"(Due: {task['due_date']})" if task["due_date"] else ""
            print(f"{task['id']}. {task['title']} {due} - {status}")
