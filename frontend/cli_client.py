import socketio
import time

class SocketIOClient:
    def __init__(self, server_url: str):
        self.sio = socketio.Client(logger=True, engineio_logger=True)
        self.server_url = server_url

        self.sio.on('connect', self.on_connect)
        self.sio.on('disconnect', self.on_disconnect)
        self.sio.on('chat_message', self.on_chat_message)

    def on_connect(self):
        print("Connected to server.")

    def on_disconnect(self):
        print("Disconnected from server.")

    def on_chat_message(self, data):
        print(f"Server: {data}")

    def start(self):
        max_retries = 3
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
                    msg = input("You: ")
                    if msg.lower() == "exit":
                        break
                    self.sio.emit("chat_message", msg)
        except KeyboardInterrupt:
                print("\nInterrupted by user.")
        finally:
                self.sio.disconnect()

if __name__ == "__main__":
    client = SocketIOClient("http://localhost:8080")
    client.start()
