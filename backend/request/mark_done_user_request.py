class MarkDoneUserRequest:
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
            task_id = input("Enter task ID to mark as done: ")       
            
        return MarkDoneUserRequest(user_id, task_service, genai_client, task_id)
    
    async def handle(self):
        task = await self.task_service.get_task_by_id(self.task_id)
        if task:
            await self.task_service.update_task(self.task_id, {"done": True})
            print("Task marked as done!")
        else:
            print("Task not found.")
                