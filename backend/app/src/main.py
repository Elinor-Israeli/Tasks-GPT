import os
import argparse
import asyncio
from dotenv import load_dotenv

from src.utils.logger import logger  
from src.socketio_server import SocketIOServer
from src.http_services.user_http_service import UserHttpService
from src.http_services.task_http_service import TaskHttpService
from src.commands.user_request import UserRequest
from src.commands.user_request_factory import UserRequestFactory
from src.http_services.http_client import HttpClient
from src.vector_store.qdrant_client import get_qdrant_client
from src.vector_store.text_embedder import TextEmbedder
from src.vector_store.task_vector_store import TaskVectorStore
from src.communicator import Communicator, CLICommunicator


from src.genai import AICommandInterpreter
from src.utils.menus import MenuChoice

load_dotenv()
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

if not GEMINI_API_KEY:
    logger.error("ERROR: GEMINI_API_KEY not found! Please set it in your .env file.")
    exit(1)

async def login_or_signup(user_service: UserHttpService, communicator:Communicator):
    logger.debug("👤 ENTERED login_or_signup()")
    await communicator.output("\n--- Login or Signup ---")
    username = (await communicator.input("Enter your username: ")).strip()
    user = await user_service.get_user_by_username(username)

    if user:
        await communicator.output(f"Welcome back to TaskGPT, {user['username']}!")
        return user['id']
    else:
        password = await communicator.input("Please enter your password: ")
        new_user = await user_service.create_user({"username": username, "password": password})
        await communicator.output(f"Welcome to TaskGPT {new_user['username']}!")
        return new_user['id']

async def main(communicator=None):
    logger.debug("⚡ ENTERED main()")

    logger.debug("initialize http client")
    http_client = HttpClient()
    user_service = UserHttpService(http_client)
    task_service = TaskHttpService(http_client)

    logger.debug("initialize genai client")
    genai_client = AICommandInterpreter(api_key=GEMINI_API_KEY)

    logger.debug("initialize qdrant client")
    qdrant_client = get_qdrant_client()
    logger.debug("initialize text embedder")
    embedder = TextEmbedder()

    vector_store = TaskVectorStore(client=qdrant_client, embedder=embedder)

    user_id = await login_or_signup(user_service, communicator)

    factory = UserRequestFactory(task_service, user_service, genai_client, user_id, vector_store)

    
    while True:
        try:
            await communicator.output("\n--- To-Do List ---\n")
            options = """
            1. View Tasks
            2. Add Task
            3. Mark Task as Done
            4. Delete Task
            5. Edit Task
            """
            await communicator.output(options)

            user_input = (await communicator.input("What would you like to do? ")).strip()

            choice = genai_client.interpret_command(user_input, options) 

            if choice == MenuChoice.NONE:
                await communicator.output("I'm sorry, I didn't understand you how could I help you?")
                continue

            request: UserRequest = await factory.create_request(choice, user_input, communicator)

            if not request:
                await communicator.output("Invalid option or command not understood. Please try again.")
                continue
            
            await request.handle(task_service, vector_store, communicator)
        
        except Exception as e:
            logger.error(f"Unexpected error occurred: {e}")
            await communicator.output("⚠️ Something went wrong. Please try again.")   
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--socket', action='store_true')
    args = parser.parse_args()

    if args.socket:
        server = SocketIOServer(handler=main)
        server.run()
    else:
        communicator = CLICommunicator()
        asyncio.run(main(communicator))