import json
from datetime import datetime, timezone
from aiokafka import AIOKafkaConsumer
from app.repositories.sensor_repository import save_aggregated_sensor_data

# Parameters for aggregation
BATCH_SIZE = 5
TEMPERATURE_THRESHOLD = 80.0  # If average temperature exceeds this, an alert is raised
buffer = []  # Buffer to store incoming sensor data

async def process_buffer():
    """Aggregate the buffered sensor data and save the augmented result to Elasticsearch."""
    if not buffer:
        return
    count = len(buffer)
    total_temp = sum(item.get("temperature", 0) for item in buffer)
    total_humidity = sum(item.get("humidity", 0) for item in buffer)
    avg_temp = total_temp / count
    avg_humidity = total_humidity / count
    min_temp = min(item.get("temperature", 0) for item in buffer)
    max_temp = max(item.get("temperature", 0) for item in buffer)
    
    # Augment the aggregated data with additional info and alert flag
    aggregated_data = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "count": count,
        "avg_temperature": avg_temp,
        "avg_humidity": avg_humidity,
        "min_temperature": min_temp,
        "max_temperature": max_temp,
        "alert": avg_temp > TEMPERATURE_THRESHOLD,
        "raw_data": buffer.copy() 
    }
    
    # Save aggregated data to Elasticsearch
    await save_aggregated_sensor_data(aggregated_data)
    print("Saved aggregated data:", aggregated_data)
    
    # Clear the buffer after processing
    buffer.clear()

async def consume_sensor_data():
    """
    Consume sensor data from Kafka, aggregate data in batches, and save augmented results.
    """
    consumer = AIOKafkaConsumer(
        "sensor_data_topic",
        bootstrap_servers="localhost:9092",
        group_id="sensor_consumer_group"
    )
    await consumer.start()
    try:
        async for msg in consumer:
            # Decode and parse the sensor message
            data = json.loads(msg.value.decode("utf-8"))
            buffer.append(data)
            # Once the buffer reaches the batch size, process the aggregation
            if len(buffer) >= BATCH_SIZE:
                await process_buffer()
    except Exception as e:
        print("Error in Kafka consumer:", e)
    finally:
        # Process any remaining messages before shutting down
        if buffer:
            await process_buffer()
        await consumer.stop()