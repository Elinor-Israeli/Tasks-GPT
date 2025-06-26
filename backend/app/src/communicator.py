from abc import ABC, abstractmethod
import asyncio
from src.utils.logger import logger

class Communicator(ABC):
    @abstractmethod
    def input(self, text: str) -> str:
        """
        This function send a text to the user requesting for input and then returns the input by the user
        This function may raise Exception in the following cases:
        - empty text
        - failure to send or receive message from user
        - timeout exception if user doesn't answer in a while (in the future) 
        """
        pass

    @abstractmethod
    def output(self, text: str):
        pass

class SocketIoCommunicator(Communicator):
    def __init__(self, sio, sid, loop):
        self.sio = sio
        self.sid = sid
        self.queue = asyncio.Queue()
        self.loop = loop or asyncio.get_event_loop()
    
    async def input(self, text: str) -> str:
        logger.debug("input() sending prompt to client")
        await self.sio.emit("chat_message", text, to=self.sid)
        logger.debug("input() waiting for response from queue...")
        response = await self.queue.get()
        logger.debug(f"input() received: {response}")
        return response

    async def output(self, text: str):
        logger.debug(f"output() sending: {text}")
        await self.sio.emit("chat_message", text, to=self.sid)

    def add_message_to_queue(self, text: str):
        logger.debug(f"Putting response in queue: {text}")
        self.loop.call_soon_threadsafe(self.queue.put_nowait, text)



class CLICommunicator(Communicator):
    async def input(self, text: str) -> str:
        return input(text) 
    
    async def output(self, text: str):
        print(text) 