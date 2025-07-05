"""
Communication interface module for the TaskGPT application.

This module provides abstract interfaces for user communication
including CLI and Socket.IO implementations.
"""

from abc import ABC, abstractmethod
import asyncio
from typing import Optional
from src.utils.logger import logger

class Communicator(ABC):
    """
    Abstract base class for user communication interfaces.
    
    This class defines the interface for all communication methods
    used to interact with users in the TaskGPT application.
    """
    
    @abstractmethod
    async def input(self, text: str) -> str:
        """
        Send a prompt to the user and receive their input.
        
        This function sends a text prompt to the user requesting input
        and then returns the input provided by the user.
        
        Args:
            text: Prompt text to display to the user
            
        Returns:
            User's input string
            
        Raises:
            Exception: If communication fails or times out
        """
        pass

    @abstractmethod
    async def output(self, text: str) -> None:
        """
        Send output text to the user.
        
        Args:
            text: Text to display to the user
        """
        pass

class SocketIoCommunicator(Communicator):
    """
    Socket.IO implementation of the communicator interface.
    
    This class provides real-time communication capabilities
    for web-based clients using Socket.IO.
    
    Attributes:
        sio: Socket.IO server instance
        sid: Session ID for the client
        queue: Async queue for message handling
        loop: Event loop for async operations
    """
    
    def __init__(self, sio, sid: str, loop: Optional[asyncio.AbstractEventLoop] = None) -> None:
        self.sio = sio
        self.sid: str = sid
        self.queue: asyncio.Queue = asyncio.Queue()
        self.loop: asyncio.AbstractEventLoop = loop or asyncio.get_event_loop()
    
    async def input(self, text: str) -> str:
        """
        Send a prompt to the client and wait for response.
        
        Args:
            text: Prompt text to send to the client
            
        Returns:
            Client's response string
        """
        logger.debug("input() sending prompt to client")
        await self.sio.emit("chat_message", text, to=self.sid)
        logger.debug("input() waiting for response from queue...")
        response: str = await self.queue.get()
        logger.debug(f"input() received: {response}")
        return response

    async def output(self, text: str) -> None:
        """
        Send output text to the client.
        
        Args:
            text: Text to send to the client
        """
        logger.debug(f"output() sending: {text}")
        await self.sio.emit("chat_message", text, to=self.sid)

    def add_message_to_queue(self, text: str) -> None:
        """
        Add a message to the response queue.
        
        This method is called by the Socket.IO event handler
        to add client responses to the queue.
        
        Args:
            text: Message text to add to the queue
        """
        logger.debug(f"Putting response in queue: {text}")
        self.loop.call_soon_threadsafe(self.queue.put_nowait, text)



class CLICommunicator(Communicator):
    """
    Command-line interface implementation of the communicator.
    
    This class provides simple console-based communication
    for CLI users of the TaskGPT application.
    """
    
    async def input(self, text: str) -> str:
        """
        Display a prompt and get user input from console.
        
        Args:
            text: Prompt text to display
            
        Returns:
            User's input string
        """
        return input(text) 
    
    async def output(self, text: str) -> None:
        """
        Display output text to the console.
        
        Args:
            text: Text to display
        """
        print(text) 