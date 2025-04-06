import asyncio
import json
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer

BANDWIDTH_THRESHOLD = 800  # Mbps
PACKET_LOSS_THRESHOLD = 2    # Percent
LATENCY_THRESHOLD = 80       # ms

# Multipliers for aggregated data (used in stream_consumer logic)
BANDWIDTH_UNHEALTHY_MULTIPLIER = 1.2
PACKET_LOSS_UNHEALTHY_MULTIPLIER = 1.5
LATENCY_UNHEALTHY_MULTIPLIER = 1.2

def determine_status(bandwidth: float, packet_loss: float, latency: float, alert_mode: bool = False) -> str:
    """
    Determine the status of a switch (or an aggregated group) based on its metrics.
    
    When alert_mode is True, any metric exceeding its threshold returns "unhealthy".
    Otherwise (for aggregated data):
      - If any metric exceeds its base threshold, then:
           * If any metric is more severe (exceeding the threshold multiplied by a factor),
             returns "unhealthy".
           * Otherwise, returns "warning".
      - Returns "healthy" if no thresholds are exceeded.
    """
    if alert_mode:
        if bandwidth > BANDWIDTH_THRESHOLD or packet_loss > PACKET_LOSS_THRESHOLD or latency > LATENCY_THRESHOLD:
            return "unhealthy"
        return "healthy"
    else:
        if bandwidth > BANDWIDTH_THRESHOLD or packet_loss > PACKET_LOSS_THRESHOLD or latency > LATENCY_THRESHOLD:
            if (bandwidth > BANDWIDTH_THRESHOLD * BANDWIDTH_UNHEALTHY_MULTIPLIER or 
                packet_loss > PACKET_LOSS_THRESHOLD * PACKET_LOSS_UNHEALTHY_MULTIPLIER or 
                latency > LATENCY_THRESHOLD * LATENCY_UNHEALTHY_MULTIPLIER):
                return "unhealthy"
            return "warning"
        return "healthy"


async def kafka_stream_processor():
    bootstrap_servers = "kafka:9092"
    source_topic = "switch_data_topic"   # The topic with raw switch data
    alerts_topic = "alerts_topic"          # Topic for unhealthy switch data
    healthy_topic = "healthy_topic"        # Topic for healthy switch data

    # Create consumer for reading switch data
    consumer = AIOKafkaConsumer(
        source_topic,
        bootstrap_servers=bootstrap_servers,
        group_id="kafka_stream_group",
        value_deserializer=lambda v: json.loads(v.decode("utf-8"))
    )

    # Create producer to publish messages to appropriate topics
    producer = AIOKafkaProducer(
        bootstrap_servers=bootstrap_servers,
        value_serializer=lambda v: json.dumps(v).encode("utf-8")
    )

    await consumer.start()
    await producer.start()

    try:
        async for msg in consumer:
            message = msg.value

            # Determine the status using your thresholds utility.
            # Here, alert_mode=True means that any breach will classify the switch as "unhealthy".
            status = determine_status(
                message.get("bandwidth_usage", 0),
                message.get("packet_loss", 0),
                message.get("latency", 0),
                alert_mode=True
            )

            # Append the computed status to the message
            message["status"] = status

            if status == "unhealthy":
                # Send message to alerts_topic
                await producer.send_and_wait(alerts_topic, message)
                print(f"Sent alert for switch {message.get('switch_id')}")
            else:
                # Send message to healthy_topic
                await producer.send_and_wait(healthy_topic, message)
                print(f"Sent healthy data for switch {message.get('switch_id')}")
    except Exception as e:
        print("Error in kafka stream processor:", e)
    finally:
        await consumer.stop()
        await producer.stop()

if __name__ == '__main__':
    asyncio.run(kafka_stream_processor())