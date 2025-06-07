from datetime import datetime

class AddTaskUserRequest:
    def __init__(self, user_id, task_service, genai_client, title, due_date):
        self.user_id = user_id
        self.task_service = task_service
        self.genai_client = genai_client
        self.title = title  
        self.due_date = due_date 

    @classmethod
    def create(cls, user_id, task_service, genai_client, user_input:str):
        extraction = genai_client.extract_task_data(user_input)
        title = extraction.get("name")
        due_date = extraction.get("date")

        print(f"[DEBUG] AI extracted: title={title}, date={due_date}")

        if not title:
            title = input("Enter task title: ")

        if not due_date or due_date.lower() == "none":
            due_date = input("Enter due date (YYYY-MM-DD): ")

        return AddTaskUserRequest(user_id, task_service, genai_client, title, due_date)

    async def handle(self):
            try:
                datetime.strptime(self.due_date, "%Y-%m-%d")
                await self.task_service.create_task({
                    "title": self.title,
                    "due_date": self.due_date,
                    "user_id": self.user_id
                })
                print("Task added!")
                return
            except ValueError:
                print("Invalid date format. Task not added.")

        