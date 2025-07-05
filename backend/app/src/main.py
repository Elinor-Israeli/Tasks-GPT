"""
Main entry point for the TaskGPT application.

This module initializes the application with command line argument parsing,
environment configuration, and starts either the Socket.IO server or CLI interface.
"""

import os
import argparse
import asyncio
from dotenv import load_dotenv
from typing import Optional

from src.utils.logger import logger  
from src.socketio_server import SocketIOServer
from src.communicator import CLICommunicator
from src.app_services import AppService

load_dotenv()
    
if __name__ == "__main__":
    parser: argparse.ArgumentParser = argparse.ArgumentParser()
    parser.add_argument('-s', '--socket', action='store_true')
    args: argparse.Namespace = parser.parse_args()

    api_base_url: str = os.getenv("API_BASE_URL", "http://localhost:8000")
    qdrant_host: str = os.getenv("QDRANT_HOST", "localhost")
    genai_key: Optional[str] = os.getenv("GEMINI_API_KEY")

    if not genai_key:
        logger.error("ERROR: GEMINI_API_KEY not found! Please set it in your .env file.")
        exit(1)

    app_service: AppService = AppService(api_base_url, qdrant_host, genai_key)

    if args.socket:
        server: SocketIOServer = SocketIOServer(handler=app_service.handle)
        server.run()
    else:
        communicator: CLICommunicator = CLICommunicator()
        asyncio.run(app_service.handle(communicator))