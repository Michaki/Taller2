import json
from datetime import datetime
from aiokafka import AIOKafkaConsumer
from app.api.endpoints.websocket import manager
from app.utils.thresholds import determine_status
from app.repositories.switch_repository import save_alert_log, save_switch_data

async def consume_topics_for_websocket():
    """
    Consumes messages from topics (alerts_topic and healthy_topic),
    persists each message to Elasticsearch, and broadcasts both
    the data update and topology update over WebSockets.
    """
    topics = ["alerts_topic", "healthy_topic"]
    consumer = AIOKafkaConsumer(
        *topics,
        bootstrap_servers="localhost:9093",  # Use external listener if backend is on host
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

            # Persist the message to Elasticsearch based on its topic
            if msg.topic == "alerts_topic":
                await save_alert_log(message)
            elif msg.topic == "healthy_topic":
                await save_switch_data(message)

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