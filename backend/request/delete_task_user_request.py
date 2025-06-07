class DeleteTaskUserRequest:
    def __init__(self, user_id, task_service, genai_client, task_id):
        self.user_id = user_id
        self.task_service = task_service
        self.genai_client = genai_client
        self.task_id = task_id

    @classmethod
    def create(cls, user_id, task_service, genai_client, user_input):
        task_id = genai_client.extract_task_id(user_input)
        print(f"[DEBUG] AI extracted task_id={task_id}")

        if not task_id:
            task_id = input("Enter task ID to delete: ")

        return DeleteTaskUserRequest(user_id, task_service, genai_client, task_id)

    async def handle(self):
        await self.task_service.delete_task(int(self.task_id))
        print("Task deleted!")
