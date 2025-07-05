"""
CLI client module for the TaskGPT application.

This module provides a command-line client for connecting to the
TaskGPT Socket.IO server and interacting with the application.
"""

import socketio
import time
from typing import Optional

class SocketIOClient:
    """
    Socket.IO client for connecting to the TaskGPT server.
    
    This class provides a command-line interface for connecting to
    the TaskGPT Socket.IO server and sending/receiving messages.
    
    Attributes:
        sio: Socket.IO client instance
        server_url: URL of the server to connect to
    """
    
    def __init__(self, server_url: str) -> None:
        self.sio: socketio.Client = socketio.Client()
        self.server_url: str = server_url

        self.sio.on('connect', self.on_connect)
        self.sio.on('disconnect', self.on_disconnect)
        self.sio.on('chat_message', self.on_chat_message)

    def on_connect(self) -> None:
        print("Connected to server.")

    def on_disconnect(self) -> None:
        print("Disconnected from server.")

    def on_chat_message(self, data: str) -> None:
        print(data)

    def start(self) -> None:
        """
        Start the client and begin the interactive session.
        
        This method attempts to connect to the server with retry logic,
        then enters an interactive loop for sending messages.
        """
        max_retries: int = 3
        for attempt in range(max_retries):
            try:
                print(f"Connecting to {self.server_url} (Attempt {attempt + 1})...")
                self.sio.connect(self.server_url)
                break
            except Exception as e:
                print(f"Connection attempt {attempt + 1} failed: {e}")
                time.sleep(2 ** attempt)
        else:
            print("Failed to connect after multiple attempts. Exiting.")
            return  
        print("Type your message below. Type 'exit' to quit.")       
        try:
            while True:
                    msg: str = input()
                    if msg.lower() == "exit":
                        break
                    self.sio.emit("chat_message", msg)
        except KeyboardInterrupt:
                print("\nInterrupted by user.")
        finally:
                self.sio.disconnect()

if __name__ == "__main__":
    client: SocketIOClient = SocketIOClient("http://localhost:8080")
    client.start()
