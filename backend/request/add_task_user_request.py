import httpx
from utils.logger import logger
from datetime import datetime
from backend.request.user_request import UserRequest
from client.genai import AICommandInterpreter

class AddTaskUserRequest(UserRequest):
    def __init__(self, user_id, title, due_date):
        super().__init__(user_id)
        self.title = title  
        self.due_date = due_date 

    @classmethod
    def create(cls, user_id, genai_client: AICommandInterpreter, user_input: str):

        extraction = genai_client.extract_task_data(user_input)
        title = extraction.get("name")
        due_date = extraction.get("date")

        logger.debug(f"AI extracted: title={title}, date={due_date}")

        while not title or title.lower() == "none":
            user_input = input("Great! enter your task title and due date : ").strip()
            extraction = genai_client.extract_task_data(user_input)
            title = extraction.get("name")
            due_date = extraction.get("date")
            logger.debug(f"Re-extracted: title={title}, date={due_date}")

        while not due_date or due_date.lower() == "none":
            user_input = input("Enter due date or include it in a full sentence (e.g., 'Walk dog next week'): ").strip()
            extraction = genai_client.extract_task_data(user_input)
            if not title and extraction.get("name"):
                title = extraction.get("name")
            due_date = extraction.get("date")
            logger.debug(f"Re-extracted: title={title}, date={due_date}")

        try:
            parsed_date = datetime.strptime(due_date, "%Y-%m-%d")
            due_date = parsed_date.strftime("%Y-%m-%d")
        except ValueError:
            logger.info("Invalid date format. Please use YYYY-MM-DD. Task not added.")
            return None

        return AddTaskUserRequest(user_id, title, due_date)

    async def handle(self, task_service):
        try:
            await task_service.create_task({
                "title": self.title,
                "due_date": self.due_date,
                "user_id": self.user_id
            })
            logger.info(f"Task '{self.title}' added with due date {self.due_date}!")
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 400:
                error_detail = e.response.json().get("detail", "Unknown error")
                logger.error(f"Failed to add task: {error_detail}")
            else:
                logger.error(f"Unexpected error while adding task: {e}")
