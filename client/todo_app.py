import os
from dotenv import load_dotenv

import asyncio
from client.http_services.user_http_service import UserHttpService
from client.http_services.task_http_service import TaskHttpService
from backend.request.user_request import UserRequest
from backend.factory.user_request_factory import UserRequestFactory
from client.http_services.http_client import HttpClient

from client.genai import AICommandInterpreter
from client.menu_choice import MenuChoice

load_dotenv()

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

if not GEMINI_API_KEY:
    print("ERROR: GEMINI_API_KEY not found! Please set it in your .env file.")
    exit(1)

async def login_or_signup(user_service):
    print("\n--- Login or Signup ---")
    username = input("Enter your username: ").strip()
    user = await user_service.get_user_by_username(username)

    if user:
        print(f"Welcome back, {user['username']}!")
        return user['id']
    else:
        print("Creating new user...")
        new_user = await user_service.create_user({"username": username})
        print(f"User created. Welcome, {new_user['username']}!")
        return new_user['id']

async def main():
    http_client = HttpClient()
    user_service = UserHttpService(http_client)
    task_service = TaskHttpService(http_client)
    genai_client = AICommandInterpreter(api_key=GEMINI_API_KEY)

    user_id = await login_or_signup(user_service)

    user_request = UserRequest(user_id, task_service, user_service, genai_client)

    while True:
        print("\n--- To-Do List ---\n")
        options = """
        1. View Tasks
        2. Add Task
        3. Mark Task as Done
        4. Delete Task
        5. Edit Task
        """
        print(options)

        user_input = input("What would you like to do? ").strip()

        choice = genai_client.interpret_command(user_input, options)

        request = UserRequestFactory.create_request(
            choice, user_request, user_input
        )

        if request:
            await request.handle(user_input,task_service, user_service, user_id)
        else:
            print("Invalid option or command not understood. Please try again.")

if __name__ == "__main__":
    asyncio.run(main())
