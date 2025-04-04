import random
import json
import time
from datetime import datetime, timezone
from kafka import KafkaProducer

def generate_sensor_data():
    """Generate a random sensor reading."""
    return {
        "temperature": round(random.uniform(60.0, 100.0), 2),
        "humidity": round(random.uniform(30.0, 80.0), 2),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

def main():
    # Configure Kafka producer; adjust bootstrap_servers if needed.
    producer = KafkaProducer(
        bootstrap_servers=['localhost:9092'],
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    
    topic = "sensor_data_topic"
    print(f"Starting data generation for topic '{topic}'...")
    
    try:
        while True:
            sensor_data = generate_sensor_data()
            # Publish the sensor data to Kafka
            producer.send(topic, sensor_data)
            print(f"Sent: {sensor_data}")
            # Sleep for a couple of seconds before sending the next record
            time.sleep(2)
    except KeyboardInterrupt:
        print("Data generation stopped by user.")
    finally:
        producer.flush()
        producer.close()

if __name__ == '__main__':
    main()
