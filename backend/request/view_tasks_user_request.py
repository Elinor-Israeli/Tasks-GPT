from datetime import datetime, date

class ViewTasksUserRequest:
    def __init__(self, choice):
        self.choice = choice
    
    @classmethod
    def create(cls, genai_client, user_input: str):
        view_option = """
        1. Completed Tasks
        2. Incomplete Tasks
        3. Overdue Tasks
        4. Upcoming Tasks
        5. All Tasks
        """
        view_types = genai_client.interpret_view_task_command(user_input, view_option)
        choice = view_types if view_types else input("Choose an option:\n" + view_option + "\n")
        return ViewTasksUserRequest(choice)

    async def handle(self, task_service ):
        today = date.today()
        tasks = []

        if self.choice == "1":
            tasks = await self.task_service.get_tasks(user_id=self.user_id, done=True)
        elif self.choice == "2":
            tasks = await self.task_service.get_tasks(user_id=self.user_id, done=False)
        elif self.choice == "3":
            tasks = await self.task_service.get_tasks(user_id=self.user_id)
            tasks = [
                task for task in tasks
                if not task['done'] and task.get('due_date') and datetime.fromisoformat(task['due_date']).date() < today
            ]
        elif self.choice == "4":
            tasks = await self.task_service.get_tasks(user_id=self.user_id)
            tasks = [
                task for task in tasks
                if not task['done'] and task.get('due_date') and datetime.fromisoformat(task['due_date']).date() >= today
            ]
        elif self.choice == "5":
            tasks = await self.task_service.get_tasks(user_id=self.user_id)
        else:
            tasks = await self.task_service.get_tasks(user_id=self.user_id)

        if not tasks:
            print("No tasks found for this option.")
            return

        # SORT newest first
        tasks = sorted(tasks, key=lambda x: x['id'], reverse=True)

        print("\n--- TASKS ---")
        for task in tasks:
            status = "✅" if task['done'] else "❌"
            due = f"(Due: {task['due_date']})" if task["due_date"] else ""
            print(f"{task['id']}. {task['title']} {due} - {status}")
