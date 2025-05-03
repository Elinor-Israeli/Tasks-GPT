import asyncio
from http_services.user_http_service import UserHttpService
from http_services.task_http_service import TaskHttpService
from http_services.http_client import HttpClient
from menu_choice import MenuChoice

# Login Sign-up
async def login_or_signup(user_service: UserHttpService) -> int:
    print("\n--- Login or Signup ---")
    username = input("Enter your username: ").strip()
    user = await user_service.get_user_by_username(username)
    if user:
        print(f"Welcome back, {username}!")
        return user['id']
    else:
        password = input("Enter your password: ").strip()
        new_user = await user_service.create_user({"username": username, "password": password})
        print(f"User '{username}' created!")
        return new_user['id']

# Show menu
def show_menu():
    print("\n--- To-Do List ---")
    print("1. View Tasks")
    print("2. Add Task")
    print("3. Mark Task as Done")
    print("4. Delete Task")
    print("5. View Completed Task")
    print("6. View Incomplete Task")
    print("7. Edit Task")
    print("8. View Upcoming Tasks")
    print("9. View Overdue Tasks")
    print("10. Exit")

# get tasks
async def get_tasks(user_id):
    return await task_service.get_tasks(user_id)

# View tasks
async def view_tasks(task_service,user_id):
    tasks = await task_service.get_tasks(user_id=user_id)
    for task in tasks:
        status = "✅" if task['done'] else "❌"
        due = f"(Due: {task['due_date']})" if task["due_date"] else ""
        print(f"{task['id']}. {task['title']} {due} - {status}")

# Add a task
async def add_task(task_service, title, due_date, user_id):
    await task_service.create_task({
        "title": title,
        "due_date": due_date,
        "user_id": user_id
    })
    print("Task added!")

# Edit task 
async def edit_task(user_id,task_service, task_id=None, choice=None, new_title=None, new_due_date=None):
    if task_id is None:
        task_id = input("Enter task ID to edit: ")

    task = await task_service.get_task(task_id)
    if not task:
        print("Task not found")
        return

    print(f"\nEditing Task {task['id']}:")
    print(f"Current title: {task['title']}")
    print(f"Current due date: {task.get('due_date', 'None')}")

    if choice is None:
        print("\nWhat would you like to edit?")
        print("1. Title")
        print("2. Due Date")
        print("3. Both")
        print("4. Cancel")
        choice = input("Choose an option: ")

    data = {}

    if choice == "1":
        data["title"] = new_title or input("Enter new title: ")
        print("Title updated!")

    elif choice == "2":
        new_due_date = new_due_date or input("Enter new due date (YYYY-MM-DD): ")
        try:
            datetime.strptime(new_due_date, "%Y-%m-%d")  # Validate
            data["due_date"] = new_due_date
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD.")
            return
        print("Due date updated!")

    elif choice == "3":
        data["title"] = new_title or input("Enter new title: ")
        new_due_date = new_due_date or input("Enter new due date (YYYY-MM-DD): ")
        try:
            datetime.strptime(new_due_date, "%Y-%m-%d")
            data["due_date"] = new_due_date
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD.")
            return
        print("Task updated!")

    else:
        print("Edit cancelled.")
        return

    await task_service.update_task(task_id, data)

# Mark as done
async def mark_done(task_service, user_id, task_id):
    if task_id is None:
        task_id = input("Enter task ID to mark as done: ")

    task = await task_service.get_task_by_id(task_id)
    print(f"task marked -{task}")
    if task:
        update_data = {"done": True}
        await task_service.update_task(task_id, update_data)
        print("Task marked as done!")
    else:
        print("Task not found.")


# Delete task
async def delete_task(task_service, task_id=None):
    if task_id is None:
        task_id = input("Enter task ID to delete from the list: ")

    if task_id:
        await task_service.delete_task(task_id)
        print("Task deleted!")
    else:
        print("Task not found.")
   
# View completed tasks
async def view_complete_tasks(task_service, user_id):
    tasks = await task_service.get_tasks(user_id, done=True)
    if not tasks:
        print("No completed tasks.")
    else:
        for task in tasks:
            print(f"{task['id']}. {task['title']} ✅")

# View incomplete tasks
async def view_incomplete_tasks(task_service, user_id):
    tasks = await task_service.get_tasks(user_id, done=False)
    if not tasks:
        print("No incomplete tasks.")
    else:
        for task in tasks:
            due = f"(Due: {task['due_date']})" if task['due_date'] else ""
            print(f"{task['id']}. {task['title']} {due} ❌")

#View upcoming tasks
async def view_upcoming_tasks(task_service, user_id):
    tasks = await task_service.get_tasks(user_id)
    today = date.today().isoformat()
    upcoming = [task for task in tasks if not task['done'] and task['due_date'] and task['due_date'] >= today]
    
    if not upcoming:
        print("No upcoming tasks.")
    else:
        print("\n--- Upcoming Tasks ---")
        for task in sorted(upcoming, key=lambda t: t['due_date']):
            print(f"{task['id']}. {task['title']} (Due: {task['due_date']}) ❌")

#View overdue tasks
async def view_overdue_tasks(task_service, user_id):
    tasks = await task_service.get_tasks(user_id)
    today = date.today().isoformat()
    overdue = [task for task in tasks if not task['done'] and task['due_date'] and task['due_date'] < today]
    
    if not overdue:
        print("No overdue tasks!")
    else:
        print("\n--- Overdue Tasks ---")
        for task in sorted(overdue, key=lambda t: t['due_date']):
            print(f"{task['id']}. {task['title']} (Due: {task['due_date']}) ⚠️")


# Main loop
async def main():
    if __name__ == "__main__":
        client = HttpClient(base_url="http://localhost:8000")
        task_service = TaskHttpService(client)
        user_service = UserHttpService(client)
        user_id = await login_or_signup(user_service)
        while True:
            show_menu()
            choice = input("What would you like to do?")
            if choice == MenuChoice.VIEW_TASKS:
               await view_tasks(task_service, user_id)
            elif choice == MenuChoice.ADD_TASK:
                title = input("Enter task title: ")
                due_date = input("Enter due date (YYYY-MM-DD): ")
                await add_task(task_service, title, due_date, user_id)
            elif choice == MenuChoice.MARK_DONE:
                await mark_done(task_service, user_id, task_id=None)
            elif choice == MenuChoice.DELETE_TASK:
                await delete_task(task_service, task_id=None)  
            elif choice == MenuChoice.VIEW_COMPLETED:
                await view_complete_tasks(task_service, user_id) 
            elif choice == MenuChoice.VIEW_INCOMPLETE:
                await view_incomplete_tasks(task_service, user_id)   
            elif choice == MenuChoice.EDIT_TASK:
                await edit_task(task_service, user_id) 
            elif choice ==MenuChoice.VIEW_UPCOMING:
                await view_upcoming_tasks(task_service, user_id)
            elif choice == MenuChoice.VIEW_OVERDUE:
                await view_overdue_tasks(task_service, user_id)           
            elif choice == MenuChoice.EXIT:
                break
            else:
                print("Invalid option. Try again!")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())