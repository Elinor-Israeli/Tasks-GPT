from models import SessionLocal, User, Task, init_db
from datetime import datetime, date

session = SessionLocal()

if __name__ == "__main__":
    init_db()

# Login Sign-up
def login_or_signup():
    print("\n--- Login or Signup ---")
    username = input("Enter your username: ").strip()

    user = session.query(User).filter_by(username=username).first()

    if user:
        print(f"Welcome back, {username}!")
        return user.id
    else:
        new_user = User(username=username)
        session.add(new_user)
        session.commit()
        print(f"User '{username}' created!")
        return new_user.id

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
def get_tasks(session, user_id):
    return session.query(Task).filter_by(user_id=user_id).all()

# View tasks
def view_tasks(session, user):
    tasks = get_tasks(session, user_id)
    for task in tasks:
        status = "✅" if task.done else "❌"
        due = f"(Due: {task.due_date})" if task.due_date else ""
        print(f"{task.id}. {task.title} {due} - {status}")

# Add a task
def add_task(session, title, due_date, user: User):
    if isinstance(due_date, str):
         try:
            due_date = datetime.strptime(due_date, "%Y-%m-%d").date()
         except ValueError:
            print("Invalid date format. Use YYYY-MM-DD.")
            return
            
    new_task = Task(title=title, due_date=due_date, user_id=user_id)
    session.add(new_task)
    session.commit()
    print("Task added!")

# Edit a task
def edit_task(session, user_id, task_id=None, choice=None, new_title=None, new_due_date=None):
    if task_id is None:
        task_id = input("Enter task ID to edit: ")

    task = session.query(Task).filter_by(id=task_id, user_id=user_id).first()
    if not task:
        print("Task not found")
        return

    print(f"\nEditing Task {task.id}:")
    print(f"Current title: {task.title}")
    print(f"Current due date: {task.due_date}")

    if choice is None:
        print("\nWhat would you like to edit?")
        print("1. Title")
        print("2. Due Date")
        print("3. Both")
        print("4. Cancel")
        choice = input("Choose an option: ")

    if choice == "1":
        task.title = new_title or input("Enter new title: ")
        print("Title updated!")

    elif choice == "2":
        new_due_date = new_due_date or input("Enter new due date (YYYY-MM-DD): ")
        if isinstance(new_due_date, str):
            try:
                new_due_date = datetime.strptime(new_due_date, "%Y-%m-%d").date()
            except ValueError:
                print("Invalid date format. Please use YYYY-MM-DD.")
                return
        task.due_date = new_due_date
        print("Due date updated!")

    elif choice == "3":
        task.title = new_title or input("Enter new title: ")
        new_due_date = new_due_date or input("Enter new due date (YYYY-MM-DD): ")
        if isinstance(new_due_date, str):
            try:
                new_due_date = datetime.strptime(new_due_date, "%Y-%m-%d").date()
            except ValueError:
                print("Invalid date format. Please use YYYY-MM-DD.")
                return
        task.due_date = new_due_date
        print("Task updated!")

    else:
        print("Edit cancelled.")
        return

    session.commit()


# Mark as done
def mark_done(session, user_id, task_id=None):
    if task_id is None:
        task_id = input("Enter task ID to mark as done: ")

    task = session.query(Task).filter_by(id=task_id, user_id=user_id).first()
    if task:
        task.done = True
        session.commit()
        print("Task marked as done!")
    else:
        print("Task not found.")

# Delete task
def delete_task(session, user_id, task_id=None):
    if task_id is None:
        task_id = input("Enter task ID to delete from the list: ")
    task = session.query(Task).filter_by(id=task_id, user_id=user_id).first()
    if task:
        session.delete(task)
        session.commit()
        print("Task deleted!")
    else:
        print("Task not found.")
   
# View completed tasks
def view_complete_tasks(session, user_id):
    tasks = session.query(Task).filter_by(user_id=user_id, done=True).all()
    if not tasks: 
        print("No completed tasks.")
    for task in tasks:
        print(f"{task.id}. {task.title} ✅")

# View incomplete tasks
def view_incomplete_tasks(session, user_id):
    tasks = session.query(Task).filter_by(user_id=user_id, done=False).all()
    if not tasks: 
        print("No incomplete tasks.")
    else:
        for task in tasks:
            due = f"(Due: {task.due_date})" if task.due_date else ""
            print(f"{task.id}. {task.title} {due} ❌")

#View upcoming tasks
def view_upcoming_tasks(session, user_id):
    today = date.today().isoformat()
    tasks = session.query(Task)\
        .filter(Task.user_id == user_id, Task.done == False, Task.due_date >=today)\
        .order_by(Task.due_date).all()    
    if not tasks: 
        print("No upcoming tasks.")
    else:
        print("\n--- Upcoming Tasks ---")
        for task in tasks:
            print(f"{task.id}. {task.title} (Due: {task.due_date}) ❌") 

#View overdue tasks
def view_overdue_tasks(session, user_id):
    today = date.today().isoformat()
    tasks = session.query(Task)\
        .filter(Task.user_id == user_id, Task.done == False, Task.due_date < today)\
        .order_by(Task.due_date).all()    
    if not tasks: 
        print("No overdue tasks!")
    else:
        print("\n--- overdue Tasks ---")
        for task in tasks:
            print(f"{task.id}. {task.title} (Due: {task.due_date}) ⚠️") 


# Main loop
if __name__ == "__main__":
    user_id = login_or_signup()
    while True:
        show_menu()
        choice = input("Choose an option: ")
        if choice == "1":
            view_tasks(session, user_id)
        elif choice == "2":
            title = input("Enter task title: ")
            due_date = input("Enter due date (YYYY-MM-DD): ")
            add_task(session, title, due_date, user_id)
        elif choice == "3":
            mark_done(session, user_id)
        elif choice == "4":
            delete_task(session, user_id)  
        elif choice == "5":
            view_complete_tasks(session, user_id) 
        elif choice == "6":
            view_incomplete_tasks(session, user_id)   
        elif choice == "7":
            edit_task(session, user_id) 
        elif choice == "8":
            view_upcoming_tasks(session, user_id)
        elif choice == "9":
            view_overdue_tasks(session, user_id)           
        elif choice == "10":
            break
        else:
            print("Invalid option. Try again!")

session.close()
