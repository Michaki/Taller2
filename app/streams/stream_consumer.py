# stream_consumer.py
import json
from datetime import datetime, timezone
from aiokafka import AIOKafkaConsumer
from app.services.alert_service import process_switch_message
from app.repositories.switch_repository import save_aggregated_switch_data
from app.api.endpoints.websocket import manager
from app.utils.thresholds import determine_status

# Global buffer to group messages by parent_switch_id
buffer = {}

# Threshold to trigger aggregation for a given parent
AGGREGATION_THRESHOLD = 5

async def process_buffer_for_parent(parent_id: str):
    """
    Aggregates buffered messages for a given parent_switch_id,
    computes average metrics and status, persists the aggregated data,
    and clears the buffer for that parent.
    """
    records = buffer.get(parent_id, [])
    if not records:
        return

    count = len(records)
    total_bandwidth = sum(record["bandwidth_usage"] for record in records)
    total_packet_loss = sum(record["packet_loss"] for record in records)
    total_latency = sum(record["latency"] for record in records)
    
    avg_bandwidth = total_bandwidth / count
    avg_packet_loss = total_packet_loss / count
    avg_latency = total_latency / count

    status = determine_status(avg_bandwidth, avg_packet_loss, avg_latency)
    alert_flag = status != "healthy"

    aggregated_data = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "parent_switch_id": parent_id,
        "count": count,
        "avg_bandwidth": avg_bandwidth,
        "avg_packet_loss": avg_packet_loss,
        "avg_latency": avg_latency,
        "status": status,
        "alert": alert_flag,
        "raw_data": records.copy()  # Optionally include raw messages for reference
    }
    # Persist aggregated data to Elasticsearch
    await save_aggregated_switch_data(aggregated_data)
    # Clear the buffer for this parent
    buffer[parent_id] = []

async def consume_switch_data():
    """
    Consumes messages from Kafka, processes each message for alerts,
    aggregates messages by parent_switch_id, and persists aggregated records.
    """
    consumer = AIOKafkaConsumer(
        "switch_data_topic",
        bootstrap_servers="localhost:9092",
        group_id="switch_consumer_group"
    )
    await consumer.start()
    try:
        async for msg in consumer:
            message = json.loads(msg.value.decode("utf-8"))
            # Process the incoming message for potential alert conditions
            alert = process_switch_message(message)
            if alert:
                # Broadcast the alert via WebSocket to all connected clients
                await manager.broadcast(alert)
                print(f"Broadcasted alert: {alert}")
            # Group messages by parent_switch_id
            parent_id = message.get("parent_switch_id")
            if not parent_id:
                continue  # Skip messages without a parent_switch_id
            buffer.setdefault(parent_id, []).append(message)
            # When the buffer for a parent reaches the threshold, process and persist aggregated data
            if len(buffer[parent_id]) >= AGGREGATION_THRESHOLD:
                await process_buffer_for_parent(parent_id)
    except Exception as e:
        print("Error in switch consumer:", e)
    finally:
        # Process any remaining messages in all buffers before shutting down
        for parent_id in list(buffer.keys()):
            if buffer[parent_id]:
                await process_buffer_for_parent(parent_id)
        await consumer.stop()
