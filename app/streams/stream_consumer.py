import json
import asyncio
from datetime import datetime, timezone
from aiokafka import AIOKafkaConsumer
from app.repositories.switch_repository import save_aggregated_switch_data

# Buffer will now be a dictionary keyed by parent_switch_id
buffer = {}

# Define thresholds for status determination
BANDWIDTH_THRESHOLD = 800  # Example value in Mbps
PACKET_LOSS_THRESHOLD = 2  # in percentage
LATENCY_THRESHOLD = 80     # in ms

def determine_status(avg_bandwidth: float, avg_packet_loss: float, avg_latency: float) -> str:
    # A simple rule: if any metric exceeds its threshold, set status to "unhealthy"; if near threshold, "warning"
    if avg_bandwidth > BANDWIDTH_THRESHOLD or avg_packet_loss > PACKET_LOSS_THRESHOLD or avg_latency > LATENCY_THRESHOLD:
        if (avg_bandwidth > BANDWIDTH_THRESHOLD * 1.2 or 
            avg_packet_loss > PACKET_LOSS_THRESHOLD * 1.5 or 
            avg_latency > LATENCY_THRESHOLD * 1.2):
            return "unhealthy"
        return "warning"
    return "healthy"

async def process_buffer_for_parent(parent_id: str):
    records = buffer[parent_id]
    count = len(records)
    total_bandwidth = sum(item["bandwidth_usage"] for item in records)
    total_packet_loss = sum(item["packet_loss"] for item in records)
    total_latency = sum(item["latency"] for item in records)
    
    avg_bandwidth = total_bandwidth / count
    avg_packet_loss = total_packet_loss / count
    avg_latency = total_latency / count

    status = determine_status(avg_bandwidth, avg_packet_loss, avg_latency)
    alert = status != "healthy"

    aggregated_data = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "parent_switch_id": parent_id,
        "count": count,
        "avg_bandwidth": avg_bandwidth,
        "avg_packet_loss": avg_packet_loss,
        "avg_latency": avg_latency,
        "status": status,
        "alert": alert,
        "raw_data": records.copy()
    }
    await save_aggregated_switch_data(aggregated_data)
    print("Saved aggregated switch data:", aggregated_data)
    buffer[parent_id] = []  # clear for that parent

async def consume_switch_data():
    consumer = AIOKafkaConsumer(
        "switch_data_topic",
        bootstrap_servers="kafka:9092",
        group_id="switch_consumer_group"
    )
    await consumer.start()
    try:
        async for msg in consumer:
            data = json.loads(msg.value.decode("utf-8"))
            parent_id = data["parent_switch_id"]
            if parent_id not in buffer:
                buffer[parent_id] = []
            buffer[parent_id].append(data)
            # Process aggregation when a batch size is reached (or based on a time interval)
            if len(buffer[parent_id]) >= 5:
                await process_buffer_for_parent(parent_id)
    except Exception as e:
        print("Error in switch consumer:", e)
    finally:
        # Process any remaining data
        for parent_id in list(buffer.keys()):
            if buffer[parent_id]:
                await process_buffer_for_parent(parent_id)
        await consumer.stop()