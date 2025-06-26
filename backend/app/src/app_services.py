import os

from src.utils.logger import logger  
from src.http_services.http_client import HttpClient
from src.http_services.user_http_service import UserHttpService
from src.http_services.task_http_service import TaskHttpService
from src.vector_store.qdrant_client import get_qdrant_client
from src.vector_store.text_embedder import TextEmbedder
from src.vector_store.task_vector_store import TaskVectorStore
from src.genai import AICommandInterpreter
from src.communicator import Communicator
from src.commands.user_request_factory import UserRequestFactory
from src.utils.menus import MenuChoice
from src.commands.user_request import UserRequest

class AppService:
    def __init__(self, api_base_url: str, qdrant_host: str, genai_key: str):

        self.http_client = HttpClient(base_url=api_base_url)
        self.user_service = UserHttpService(self.http_client)
        self.task_service = TaskHttpService(self.http_client)

        self.genai_client = AICommandInterpreter(api_key=genai_key)

        self.qdrant_client = get_qdrant_client(host=qdrant_host)
        self.embedder = TextEmbedder()
        self.vector_store = TaskVectorStore(client=self.qdrant_client, embedder=self.embedder)
    
    async def handle(self, communicator=None):

        logger.debug("Using global app_services")

        user_id = await self._login_or_signup(communicator)
        factory = UserRequestFactory(self.task_service, self.user_service, self.genai_client, user_id, self.vector_store)

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
                choice = self.genai_client.interpret_command(user_input, options) 

                if choice == MenuChoice.NONE:
                    await communicator.output("I'm sorry, I didn't understand you how could I help you?")
                    continue

                request: UserRequest = await factory.create_request(choice, user_input, communicator)

                if not request:
                    await communicator.output("Invalid option or command not understood. Please try again.")
                    continue
                
                await request.handle(self.task_service, self.vector_store, communicator)
            
            except Exception as e:
                logger.error(f"Unexpected error occurred: {e}")
                await communicator.output("⚠️ Something went wrong. Please try again.")

    async def _login_or_signup(self, communicator:Communicator):
        await communicator.output("\n--- Login or Signup ---")
        username = (await communicator.input("Enter your username: ")).strip()
        user = await self.user_service.get_user_by_username(username)

        if user:
            await communicator.output(f"Welcome back to TaskGPT, {user['username']}!")
            return user['id']
        else:
            password = await communicator.input("Please enter your password: ")
            new_user = await self.user_service.create_user({"username": username, "password": password})
            await communicator.output(f"Welcome to TaskGPT {new_user['username']}!")
            return new_user['id']
