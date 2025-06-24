from aiohttp import web
import socketio
import asyncio
from src.communicator import SocketIoCommunicator

class SocketIOServer:
    def __init__(self, handler):
        self.handler = handler
        self.sio = socketio.AsyncServer()
        self.app = web.Application()
        self.sio.attach(self.app)

        self.sio.on('connect', self.handle_connect)
        self.sio.on('disconnect', self.handle_disconnect)
        self.sio.on('chat_message', self.handle_chat_message)

        self.app.router.add_get('/', self.index)  
        # self.app.router.add_static('/static', 'static')

        self.sid_to_communicator = {}

    async def index(self, request):
        """Serve the client-side HTML (optional)."""
        return web.Response(text="Socket.IO server is running!", content_type='text/html')

    async def handle_connect(self, sid, environ):
        print("Client connected:", sid)
        communicator = SocketIoCommunicator(self.sio, sid)
        self.sid_to_communicator[sid] = communicator

        await self.handler(communicator)


    async def handle_chat_message(self, sid, data):
        print("Message received:", data)
        self.sid_to_communicator[sid].get_from_socketio(data)

    async def handle_disconnect(self, sid):
        print("Client disconnected:", sid)

    def run(self):
        web.run_app(self.app)

