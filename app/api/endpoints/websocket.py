from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from datetime import datetime

router = APIRouter()

# Global in-memory store for alert logs
alert_logs = []

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []
        
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        # Append the message to the logs with a timestamp
        alert_logs.append({"timestamp": datetime.now().isoformat(), **message})
        for connection in self.active_connections:
            await connection.send_json(message)

manager = ConnectionManager()

@router.websocket("/alerts")
async def alerts_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Here you can listen for client messages (if needed)
            data = await websocket.receive_text()
            print(f"Received data from client: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
