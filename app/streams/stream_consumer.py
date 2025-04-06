# app/streams/stream_consumer.py

import json
from aiokafka import AIOKafkaConsumer
from app.api.endpoints.websocket import manager
from app.repositories.switch_repository import save_alert_log, save_switch_data

async def consume_topics_for_websocket():
    """
    Consumes messages from two Kafka topics ("alerts_topic" and "healthy_topic"),
    persists each message to the appropriate Elasticsearch index, and broadcasts the message via WebSocket.
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
            # Persist the message to Elasticsearch based on its status:
            if msg.topic == "alerts_topic":
                await save_alert_log(message)
            else:
                await save_switch_data(message)
            # Broadcast the message to all connected WebSocket clients.
            await manager.broadcast(message)
    except Exception as e:
        print("Error in consuming topics:", e)
    finally:
        await consumer.stop()
