from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.core.websocket_manager import ConnectionManager
from app.services.sensor_service import process_sensor_data
from app.repositories.sensor_repository import get_aggregated_sensor_data_count

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

@router.websocket("/aggregated-stats")
async def aggregated_stats_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            command = await websocket.receive_text()
            if command.lower() == "stats":
                count = await get_aggregated_sensor_data_count()
                await websocket.send_text(f"Aggregated sensor data count: {count}")
            else:
                await websocket.send_text("Unknown command. Send 'stats' to get the count.")
    except WebSocketDisconnect:
        print("WebSocket disconnected")