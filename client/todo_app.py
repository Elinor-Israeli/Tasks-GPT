import asyncio
from http_services.user_http_service import UserHttpService
from http_services.task_http_service import TaskHttpService
from http_services.http_client import HttpClient
from menu_choice import MenuChoice
from datetime import datetime, date
import os
from dotenv import load_dotenv
from genai import AICommandInterpreter


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
    options = """
    1. View Tasks
    2. Add Task
    3. Mark Task as Done
    4. Delete Task
    5. Edit Task
    """
    print(options)
    return options

# get tasks
async def get_tasks(user_id):
    return await task_service.get_tasks(user_id)

async def view_tasks(task_service, user_id, choice=None):
    if choice is None:
        print("\nWhat kind of Tasks would you like to view? ")
        print("1. Complete Tasks")
        print("2. Incomplete Tasks")
        print("3. Overdue Tasks")
        print("4. Upcoming Tasks")
        print("5. All Tasks")
        choice = input("Choose an option: ")

    if choice == "1":
        tasks = await task_service.get_tasks(user_id=user_id, done=True)
        if not tasks:
         print("No completed tasks. Get to work!")
    elif choice == "2":
        tasks = await task_service.get_tasks(user_id=user_id, done=False)
        if not tasks:
         print("No incomplete tasks. Well done!")
    elif choice == "3":  # Overdue Tasks
        today = date.today()
        tasks = await task_service.get_tasks(user_id=user_id, due_date=today.isoformat())
        if not tasks:
         print("No overdue tasks! You have your shit together!") 
    elif choice == "4":  # Upcoming Tasks
        today = date.today()
        tasks = await task_service.get_tasks(user_id=user_id)
        upcoming = [
            task for task in tasks
            if not task['done']
            and task.get('due_date')
            and datetime.fromisoformat(task['due_date']).date() >= today
                    ]
        if not tasks:
         print("No Upcoming tasks! go watch a tv show!") 
    elif choice == "5":
        tasks = await task_service.get_tasks(user_id=user_id)
    else:
        tasks = await get_tasks_from_service(user_id=user_id)

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
async def edit_task(task_service, user_id, task_id=None, choice=None, new_title=None, new_due_date=None):
    if task_id is None:
        task_id = input("Enter task ID to edit: ")

    task = await task_service.get_task_by_id(task_id)
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
            datetime.strptime(new_due_date, "%Y-%m-%d") 
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

# Main loop
async def main():
    load_dotenv()  # take environment variables
    client = HttpClient(base_url="http://localhost:8000")
    genai_client = AICommandInterpreter(os.environ['GEMINI_API_KEY'])
    task_service = TaskHttpService(client)
    user_service = UserHttpService(client)
    user_id = await login_or_signup(user_service)
    while True:
        options = show_menu()
        user_input = input("What would you like to do? ")
        choice = genai_client.interpret_command(user_input, options)
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
        elif choice == MenuChoice.EDIT_TASK:
            await edit_task(task_service, user_id)     
        elif choice == MenuChoice.EXIT:
            break
        else:
            print("Invalid option. Try again!")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
