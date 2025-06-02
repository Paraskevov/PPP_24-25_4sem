import asyncio
import websockets
import requests
import json
from typing import Optional

SERVER_URL = "http://localhost:8000"
WS_SERVER = "ws://localhost:8000/api/v1/ws"

class WebSocketClient:
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.websocket_url = f"{WS_SERVER}/{user_id}"

    async def listen_for_updates(self):
        """Listen for WebSocket updates from the server."""
        try:
            async with websockets.connect(self.websocket_url) as ws:
                print(f"Connected to WebSocket at {self.websocket_url}")
                while True:
                    message = await ws.recv()
                    data = json.loads(message)
                    print("Update received:", data)
        except websockets.exceptions.ConnectionClosed:
            print("WebSocket connection closed")
        except Exception as e:
            print(f"WebSocket error: {e}")

    def start_parsing_task(self, url: str, depth: int):
        """Start a new parsing task."""
        try:
            response = requests.post(
                f"{SERVER_URL}/api/v1/parse/",
                json={
                    "url": url,
                    "max_depth": depth,
                    "user_id": self.user_id
                }
            )
            response.raise_for_status()
            print("Task started successfully:", response.json())
        except requests.RequestException as e:
            print(f"Failed to start task: {e}")

async def main():
    user_id = 1  # Можно изменить на ввод от пользователя
    client = WebSocketClient(user_id)
    
    url = input("Enter URL to parse: ")
    depth = int(input("Enter parsing depth: "))
    
    # Start WebSocket listener
    listener = asyncio.create_task(client.listen_for_updates())
    
    # Start parsing task
    client.start_parsing_task(url, depth)
    
    # Wait for listener to complete
    await listener

if __name__ == "__main__":
    asyncio.run(main())