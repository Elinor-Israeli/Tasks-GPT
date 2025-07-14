"""
Application service module for coordinating the main application logic.

This module contains the AppService class which orchestrates all application
components including HTTP services, AI integration, and vector storage.
"""

import os
from typing import Optional, Tuple

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
    """
    Main application service that coordinates all components.
    
    This class manages the interaction between HTTP services, AI processing,
    vector storage, and user communication. It handles the main application
    loop and user authentication flow.
    
    Attributes:
        http_client: HTTP client for API communication
        user_service: Service for user-related operations
        task_service: Service for task-related operations
        genai_client: AI command interpreter
        qdrant_client: Vector database client
        embedder: Text embedding service
        vector_store: Task vector storage service
    """
    
    def __init__(self, api_base_url: str, qdrant_host: str, genai_key: str) -> None:
        """
        Initialize the application service with all required components.
        
        Args:
            api_base_url: Base URL for the API server
            qdrant_host: Host address for Qdrant vector database
            genai_key: API key for Gemini AI service
        """
        http_client: HttpClient = HttpClient(base_url=api_base_url)
        self.user_service: UserHttpService = UserHttpService(http_client)
        self.task_service: TaskHttpService = TaskHttpService(http_client)

        self.genai_client: AICommandInterpreter = AICommandInterpreter(api_key=genai_key)

        qdrant_client = get_qdrant_client(host=qdrant_host)
        embedder: TextEmbedder = TextEmbedder()
        self.vector_store: TaskVectorStore = TaskVectorStore(client=qdrant_client, embedder=embedder)

    async def handle(self, communicator: Communicator = None) -> None:
        """
        Main application handler that manages the user interaction loop.
        
        This method handles user authentication, menu generation, command
        interpretation, and request processing in a continuous loop.
        
        Args:
            communicator: Communication interface for user interaction
        """
        logger.debug("Using global app_services")

        user_id: int
        username: str
        user_id, username = await self._login_or_signup(communicator)
        factory: UserRequestFactory = UserRequestFactory(
            task_service=self.task_service,
            user_service=self.user_service,
            genai_client=self.genai_client,
            user_id=user_id,
            vector_store=self.vector_store
        )

        first_time = True
        while True:
            try:
                menu_prompt: str = self.genai_client.generate_conversational_menu(
                    username=username,
                    first_time=first_time
                )
                first_time = False

                options: str = """
                1. View Tasks
                2. Add Task
                3. Mark Task as Done
                4. Delete Task
                5. Edit Task
                """
                user_input: str = (await communicator.input(menu_prompt)).strip()

                choice: MenuChoice = self.genai_client.interpret_command(user_input, options)

                if choice == MenuChoice.NONE:
                    await communicator.output("Hmm, I didn't quite get that. Want to try saying it differently?")
                    continue

                response: str = self.genai_client.generate_conversational_response(user_input, intent=choice)
                await communicator.output(response)

                request: Optional[UserRequest] = await factory.create_request(choice, user_input, communicator)

                if not request:
                    await communicator.output("Sorry, I couldn't figure that out. Maybe try a different phrase?")
                    continue

                success = await request.handle(self.task_service, self.vector_store, communicator)

                if success:
                    followup = self.genai_client.generate_conversational_menu(username=username, first_time=False)
                    await communicator.output(followup)
                else:
                    await communicator.output("⚠️ Something went wrong with your request. Try again!")
                    first_time = True


            except Exception as e:
                logger.error(f"Unexpected error occurred: {e}")
                await communicator.output("⚠️ Something went wrong. Please try again.")
                first_time = True

    async def _login_or_signup(self, communicator: Communicator) -> Tuple[int, str]:
        """
        Handle user authentication flow (login or signup).
        
        This method prompts the user for credentials, attempts to find
        an existing user, and creates a new account if needed.
        
        Args:
            communicator: Communication interface for user interaction
            
        Returns:
            Tuple of (user_id, username) for the authenticated user
        """
        await communicator.output("\n--- Login or Signup ---")
        username: str = (await communicator.input("Enter your username: ")).strip()
        user: Optional[dict] = await self.user_service.get_user_by_username(username)

        if user:
            await communicator.output(f"Welcome back to TaskGPT, {user['username']}! 🎉")
            return user['id'], user['username']
        else:
            password: str = await communicator.input("You're new! Please create a password: ")
            new_user: dict = await self.user_service.create_user({"username": username, "password": password})
            await communicator.output(f"Welcome to TaskGPT, {new_user['username']}! 🚀")
            return new_user['id'], new_user['username']
