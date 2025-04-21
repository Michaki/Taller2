import asyncio
import json
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer

BANDWIDTH_THRESHOLD = 800  # Mbps
PACKET_LOSS_THRESHOLD = 2   # Percent
LATENCY_THRESHOLD = 80      # ms

# Multipliers for determining "unhealthy" vs "warning"
BANDWIDTH_UNHEALTHY_MULTIPLIER = 1.2
PACKET_LOSS_UNHEALTHY_MULTIPLIER = 1.5
LATENCY_UNHEALTHY_MULTIPLIER = 1.2

def determine_status(bandwidth: float, packet_loss: float, latency: float, alert_mode: bool = False) -> str:
    """
    Determine the status of a switch based on its metrics.
    
    - alert_mode=False: distingue entre healthy / warning / unhealthy.
    """
    if alert_mode:
        if bandwidth > BANDWIDTH_THRESHOLD or packet_loss > PACKET_LOSS_THRESHOLD or latency > LATENCY_THRESHOLD:
            return "unhealthy"
        return "healthy"
    else:
        if bandwidth > BANDWIDTH_THRESHOLD or packet_loss > PACKET_LOSS_THRESHOLD or latency > LATENCY_THRESHOLD:
            # Si supera multiplicadores -> unhealthy
            if (bandwidth > BANDWIDTH_THRESHOLD * BANDWIDTH_UNHEALTHY_MULTIPLIER or 
                packet_loss > PACKET_LOSS_THRESHOLD * PACKET_LOSS_UNHEALTHY_MULTIPLIER or 
                latency > LATENCY_THRESHOLD * LATENCY_UNHEALTHY_MULTIPLIER):
                return "unhealthy"
            # Sino, warning
            return "warning"
        return "healthy"

async def kafka_stream_processor():
    bootstrap_servers = "kafka:9092"
    source_topic    = "switch_data_topic"
    healthy_topic   = "healthy_topic"
    warning_topic   = "warning_topic"   # nuevo
    combined_alerts_topic    = "alerts_topic"
    unhealthy_topic = "unhealthy_topic" # nuevo

    consumer = AIOKafkaConsumer(
        source_topic,
        bootstrap_servers=bootstrap_servers,
        group_id="kafka_stream_group",
        value_deserializer=lambda v: json.loads(v.decode("utf-8"))
    )

    producer = AIOKafkaProducer(
        bootstrap_servers=bootstrap_servers,
        value_serializer=lambda v: json.dumps(v).encode("utf-8")
    )

    await consumer.start()
    await producer.start()
    try:
        async for msg in consumer:
            message = msg.value

            # Usamos alert_mode=False para obtener healthy/warning/unhealthy
            status = determine_status(
                message.get("bandwidth_usage", 0),
                message.get("packet_loss", 0),
                message.get("latency", 0),
                alert_mode=False
            )
            message["status"] = status

            # Enrutamiento a los 3 topics
            if status == "unhealthy":
                await producer.send_and_wait(unhealthy_topic, message)
            elif status == "warning":
                await producer.send_and_wait(warning_topic, message)
            else:
                await producer.send_and_wait(healthy_topic, message)

            if status in ("warning", "unhealthy"):
               await producer.send_and_wait(combined_alerts_topic, message)

            print(f"Senta {status} for switch {message.get('switch_id')}")

    except Exception as e:
        print("Error in kafka stream processor:", e)
    finally:
        await consumer.stop()
        await producer.stop()

if __name__ == '__main__':
    asyncio.run(kafka_stream_processor())
