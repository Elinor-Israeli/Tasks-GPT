from abc import ABC, abstractmethod
import asyncio

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
    def __init__(self, sio, sid):
        self.sio = sio
        self.sid = sid
        self.queue = asyncio.Queue()
        self.message = None
        self.waiter = None
    
    async def input(self, text: str) -> str:
        self.waiter = asyncio.get_event_loop().create_future()
        await self.sio.emit("chat_message", text, to=self.sid)
        result = await self.waiter
        return result

    async def output(self, text: str):
        await self.sio.emit("chat_message", text, to=self.sid)

    def get_from_socketio(self, text: str):
        if self.waiter and not self.waiter.done():
            self.waiter.set_result(text)
        else:    
            self.message = text


class CLICommunicator(Communicator):
    async def input(self, text: str) -> str:
        return input(text) 
    
    async def output(self, text: str):
        print(text) 