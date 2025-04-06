from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.core.websocket_manager import manager
import json

router = APIRouter()

@router.websocket("/alerts")
async def alerts_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                payload = json.loads(data)
                # Assume the client can send a message like: {"subscribe": "alert"} 
                if "subscribe" in payload:
                    # Update the subscription for this websocket
                    for conn in manager.active_connections:
                        if conn["ws"] == websocket:
                            conn["subscription"] = payload["subscribe"]
                            await websocket.send_json({
                                "event": "subscription_updated",
                                "data": f"Subscribed to {payload['subscribe']}"
                            })
            except Exception as e:
                print("Error processing incoming message:", e)
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@router.websocket("/test")
async def alerts_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Optionally process client messages (e.g., subscription updates)
            print(f"Received from client: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
