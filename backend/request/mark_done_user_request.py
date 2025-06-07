class MarkDoneUserRequest:
    def __init__(self, task_id):
        self.task_id = task_id
    
    @classmethod
    def create(cls, task_id):
        task_id = input("Enter task ID to mark as done: ")
        return MarkDoneUserRequest(task_id)
    
    async def handle(self, task_service, user_service, user_id):
        
        task = await task_service.get_task_by_id(self.task_id)
        if task:
            await task_service.update_task(self.task_id, {"done": True})
            print("Task marked as done!")
        else:
            print("Task not found.")
                