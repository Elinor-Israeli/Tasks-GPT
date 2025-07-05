from abc import ABC, abstractmethod
import asyncio
from typing import Optional
from src.utils.logger import logger

class Communicator(ABC):
    @abstractmethod
    async def input(self, text: str) -> str:
        """
        This function send a text to the user requesting for input and then returns the input by the user
        This function may raise Exception in the following cases:
        - empty text
        - failure to send or receive message from user
        - timeout exception if user doesn't answer in a while (in the future) 
        """
        pass

    @abstractmethod
    async def output(self, text: str) -> None:
        pass

class SocketIoCommunicator(Communicator):
    def __init__(self, sio, sid: str, loop: Optional[asyncio.AbstractEventLoop] = None) -> None:
        self.sio = sio
        self.sid: str = sid
        self.queue: asyncio.Queue = asyncio.Queue()
        self.loop: asyncio.AbstractEventLoop = loop or asyncio.get_event_loop()
    
    async def input(self, text: str) -> str:
        logger.debug("input() sending prompt to client")
        await self.sio.emit("chat_message", text, to=self.sid)
        logger.debug("input() waiting for response from queue...")
        response: str = await self.queue.get()
        logger.debug(f"input() received: {response}")
        return response

    async def output(self, text: str) -> None:
        logger.debug(f"output() sending: {text}")
        await self.sio.emit("chat_message", text, to=self.sid)

    def add_message_to_queue(self, text: str) -> None:
        logger.debug(f"Putting response in queue: {text}")
        self.loop.call_soon_threadsafe(self.queue.put_nowait, text)



class CLICommunicator(Communicator):
    async def input(self, text: str) -> str:
        return input(text) 
    
    async def output(self, text: str) -> None:
        print(text) 