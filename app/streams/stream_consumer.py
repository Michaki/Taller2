import json
import asyncio
from aiokafka import AIOKafkaConsumer

async def consume_sensor_data():
    """
    Consume sensor data from the Kafka topic and process each message.
    """
    # Create an asynchronous Kafka consumer
    consumer = AIOKafkaConsumer(
        "sensor_data_topic",
        bootstrap_servers="localhost:9092",
        group_id="sensor_consumer_group"
    )
    
    # Start the consumer
    await consumer.start()
    try:
        # Continuously listen for new messages
        async for msg in consumer:
            # Decode and load the JSON data
            data = json.loads(msg.value.decode("utf-8"))
            # Process the data (here we simply print it)
            print("Consumed message:", data)
            # TODO: Integrate your business logic for processing sensor data
    except Exception as e:
        print("Error in Kafka consumer:", e)
    finally:
        # Ensure the consumer is closed properly
        await consumer.stop()