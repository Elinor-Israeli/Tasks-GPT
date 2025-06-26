from aiohttp import web
import socketio
import asyncio
import threading
from src.communicator import SocketIoCommunicator
from src.utils.logger import logger

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

        self.sid_to_communicator = {}

    async def index(self, request):
        """Serve the client-side HTML (optional)."""
        return web.Response(text="Socket.IO server is running!", content_type='text/html')
    async def handle_connect(self, sid, environ):
        logger.info("Client connected:", sid)

        def run_main_in_thread():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            communicator = SocketIoCommunicator(self.sio, sid, loop=loop)
            self.sid_to_communicator[sid] = communicator

            loop.run_until_complete(self.handler(communicator))
            loop.close()

        threading.Thread(target=run_main_in_thread).start()    


    async def handle_chat_message(self, sid, data):
        logger.debug(f"Received message from {sid}: {data}")
        if sid in self.sid_to_communicator:
            self.sid_to_communicator[sid].add_message_to_queue(data)

    async def handle_disconnect(self, sid):
        logger.info("Client disconnected:", sid)
        del self.sid_to_communicator[sid]

    def run(self, host="0.0.0.0", port=8080):
        web.run_app(self.app, host=host, port=port)    


