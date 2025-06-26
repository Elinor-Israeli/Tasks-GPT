import os
import argparse
import asyncio
from dotenv import load_dotenv

from src.utils.logger import logger  
from src.socketio_server import SocketIOServer
from src.communicator import CLICommunicator
from src.app_services import AppService

load_dotenv()
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--socket', action='store_true')
    args = parser.parse_args()

    api_base_url = os.getenv("API_BASE_URL", "http://localhost:8000")
    qdrant_host = os.getenv("QDRANT_HOST", "localhost")
    genai_key = os.getenv("GEMINI_API_KEY")

    if not genai_key:
        logger.error("ERROR: GEMINI_API_KEY not found! Please set it in your .env file.")
        exit(1)

    app_service = AppService(api_base_url, qdrant_host, genai_key)

    if args.socket:
        server = SocketIOServer(handler=app_service.handle)
        server.run()
    else:
        communicator = CLICommunicator()
        asyncio.run(app_service.handle(communicator))