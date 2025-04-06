import json
from datetime import datetime
from aiokafka import AIOKafkaConsumer
from app.api.endpoints.websocket import manager
from app.utils.thresholds import determine_status

async def consume_topics_for_websocket():
    """
    Consumes messages from topics (like alerts_topic and healthy_topic) and also sends a topology update.
    """
    topics = ["alerts_topic", "healthy_topic"]
    consumer = AIOKafkaConsumer(
        *topics,
        bootstrap_servers="localhost:9093",  # use external listener if backend is on host
        group_id="websocket_broadcast_group",
        value_deserializer=lambda v: json.loads(v.decode("utf-8"))
    )
    
    await consumer.start()
    try:
        async for msg in consumer:
            message = msg.value
            # Determine the switch's state (if not already computed)
            if "status" not in message:
                status = determine_status(
                    message.get("bandwidth_usage", 0),
                    message.get("packet_loss", 0),
                    message.get("latency", 0),
                    alert_mode=True
                )
                message["status"] = status

            # Broadcast the original message (alert or healthy update)
            await manager.broadcast({
                "event": "data_update",
                "data": message,
                "timestamp": datetime.now().isoformat()
            })
            # Additionally, broadcast topology updates using switch_id and parent_switch_id.
            topology_message = {
                "event": "topology_update",
                "data": {
                    "switch_id": message.get("switch_id"),
                    "parent_switch_id": message.get("parent_switch_id"),
                    "state": message.get("status")
                },
                "timestamp": datetime.now().isoformat()
            }
            await manager.broadcast(topology_message)
    except Exception as e:
        print("Error in consuming topics:", e)
    finally:
        await consumer.stop()