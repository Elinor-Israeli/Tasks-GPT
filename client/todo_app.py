import os
from dotenv import load_dotenv
from utils.logger import logger  

import asyncio
from client.http_services.user_http_service import UserHttpService
from client.http_services.task_http_service import TaskHttpService
from backend.request.user_request import UserRequest
from backend.factory.user_request_factory import UserRequestFactory
from client.http_services.http_client import HttpClient

from vector_store.interfaces import Addable
from vector_store.qdrant_client import QdrantManager
from vector_store.embedder import TextEmbedder
from vector_store.task_vector_store import TaskVectorStore


from client.genai import AICommandInterpreter
from client.menus import MenuChoice

load_dotenv()

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

if not GEMINI_API_KEY:
    logger.error("ERROR: GEMINI_API_KEY not found! Please set it in your .env file.")
    exit(1)

async def login_or_signup(user_service):
    print("\n--- Login or Signup ---")
    username = input("Enter your username: ").strip()
    user = await user_service.get_user_by_username(username)

    if user:
        print(f"Welcome back to TaskGPT, {user['username']}!")
        return user['id']
    else:
        password = input("Please enter your password: ")
        new_user = await user_service.create_user({"username": username, "password": password})
        logger.info(f"Welcome to TaskGPT {new_user['username']}!")
        return new_user['id']

async def main():
    http_client = HttpClient()
    user_service = UserHttpService(http_client)
    task_service = TaskHttpService(http_client)
    genai_client = AICommandInterpreter(api_key=GEMINI_API_KEY)

    qdrant = QdrantManager()
    embedder = TextEmbedder()
    vector_store = TaskVectorStore(client=qdrant.get_client(), embedder=embedder)

    user_id = await login_or_signup(user_service)

    factory = UserRequestFactory(task_service, user_service, genai_client, user_id, vector_store)


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

        if choice == MenuChoice.NONE:
            print("I'm sorry, I didn't understand you how could I help you?")

        request: UserRequest = await factory.create_request(choice, user_input)
        if not request:
            logger.error("Invalid option or command not understood. Please try again.")
            continue
        
        await request.handle(task_service)
            

if __name__ == "__main__":
    asyncio.run(main())
