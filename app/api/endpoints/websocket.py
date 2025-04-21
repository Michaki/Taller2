from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.core.websocket_manager import manager
import json
from app.repositories.switch_repository import (
    get_overall_metrics,
    get_alert_logs,
    get_alert_insights,
    clear_all_documents,
    get_topology,
    get_all,
    get_aggregated_bandwidth,
    get_switch_state_summary,
    get_alert_logs_count,
)

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

@router.websocket("/dashboard")
async def dashboard_ws(websocket: WebSocket):
    # Registrar la conexión
    await manager.connect(websocket)
    try:
        while True:
            # 1) Obtener datos actuales
            state_summary   = await get_switch_state_summary()
            timestamps, avg_bandwidth_trend = await get_aggregated_bandwidth()
            overall_metrics = await get_overall_metrics()
            alert_count     = await get_alert_logs_count()

            # 2) Enviar payload
            await websocket.send_json({
                "event": "aggregated",
                "data": {
                    "state_summary":       state_summary,
                    "alert_count":         alert_count,
                    "timestamps":          timestamps,
                    "avg_bandwidth_trend": avg_bandwidth_trend,
                    "overall_metrics":     overall_metrics
                }
            })

            # 3) Esperar antes de la siguiente emisión
            await asyncio.sleep(5)  # ajustar frecuencia según necesidad

    except WebSocketDisconnect:
        manager.disconnect(websocket)