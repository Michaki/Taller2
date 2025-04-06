# app/core/websocket_manager.py

from fastapi import WebSocket
from typing import List, Dict

class ConnectionManager:
    def __init__(self):
        # Each connection can include extra metadata, e.g. subscriptions.
        self.active_connections: List[Dict] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        # Store connection with default subscription (all events)
        self.active_connections.append({"ws": websocket, "subscription": "all"})
        print("Client connected. Total:", len(self.active_connections))

    def disconnect(self, websocket: WebSocket):
        self.active_connections = [
            conn for conn in self.active_connections if conn["ws"] != websocket
        ]
        print("Client disconnected. Total:", len(self.active_connections))

    async def broadcast(self, message: dict):
        # Broadcast the message to all clients that are subscribed to this event type.
        for conn in self.active_connections:
            subscription = conn.get("subscription", "all")
            if subscription == "all" or subscription == message.get("event"):
                try:
                    await conn["ws"].send_json(message)
                except Exception as e:
                    print("Error sending message:", e)

manager = ConnectionManager()
