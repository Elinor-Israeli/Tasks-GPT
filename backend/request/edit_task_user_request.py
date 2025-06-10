from datetime import datetime
from backend.request.user_request import UserRequest
from utils.logger import logger
class EditTaskUserRequest(UserRequest):
    def __init__(self, user_id, task_id, choice):
        super().__init__(user_id)
        self.task_id = task_id
        self.choice = choice
    
    @classmethod
    async def create(cls, user_id, task_service, genai_client, user_input):
        data = genai_client.extract_task_id_or_title(user_input)
        task_id = data.get("task_id")
        task_title = data.get("task_title")

        logger.debug(f"AI extracted task_id={task_id}, task_title={task_title}")

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
        choice = edit_types if edit_types else input("Choose an option:\n" + edit_options + "\n").strip()

        return EditTaskUserRequest(user_id, task_id, choice)


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
