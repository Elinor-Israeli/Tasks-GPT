from datetime import datetime

class EditTaskUserRequest:
    def __init__(self, user_id, task_service, genai_client):
        self.user_id = user_id
        self.task_service = task_service
        self.genai_client = genai_client

    @classmethod
    async def create(cls,genai_client, task_id, task_service, user_input):   
        task_id = input("Enter task ID to edit: ")
        task = await task_service.get_task_by_id(task_id)
        if not task:
            print("Task not found.")
            return   
         
        print(f"\nEditing Task {task['id']} - {task['title']}")
        edit_options = """
        1. Title
        2. Due Date
        3. Both
        4. Cancel
        """    
        edit_types = genai_client.interpret_edit_task_command(user_input, edit_options)
        choice = edit_types if edit_types else input("Choose an option:\n" + edit_options + "\n") 
        return EditTaskUserRequest(choice)
        
    async def handle(self):
        data = {}
        if self.choice == "1":
            data["title"] = input("Enter new title: ")
        elif self.choice == "2":
            new_due_date = input("Enter new due date (YYYY-MM-DD): ")
            try:
                datetime.strptime(new_due_date, "%Y-%m-%d")
                data["due_date"] = new_due_date
            except ValueError:
                print("Invalid date format. Please use YYYY-MM-DD.")
                return
        elif self.choice == "3":
            data["title"] = input("Enter new title: ")
            new_due_date = input("Enter new due date (YYYY-MM-DD): ")
            try:
                datetime.strptime(new_due_date, "%Y-%m-%d")
                data["due_date"] = new_due_date
            except ValueError:
                print("Invalid date format. Please use YYYY-MM-DD.")
                return
        else:
            print("Edit cancelled.")
            return

        await self.task_service.update_task(self.task_id, data)
        print("Task updated!")