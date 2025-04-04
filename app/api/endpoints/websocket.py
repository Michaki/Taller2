from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.core.websocket_manager import ConnectionManager
from app.services.sensor_service import process_sensor_data

router = APIRouter()
manager = ConnectionManager()

@router.websocket("/sensor-stream")
async def sensor_stream_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            # Process the incoming sensor data (validation, business logic, indexing)
            response = await process_sensor_data(data)
            # Optionally broadcast a response or alert to all connected clients
            await manager.broadcast(response)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
