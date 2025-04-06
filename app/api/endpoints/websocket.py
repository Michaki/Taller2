from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.core.websocket_manager import manager

router = APIRouter()

@router.websocket("/alerts")
async def alerts_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Optionally, you can listen for client messages (if needed)
            data = await websocket.receive_text()
            print(f"Received from client: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
