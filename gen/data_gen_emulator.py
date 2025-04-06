import random
import time
import json
from datetime import datetime, timezone
from uuid import uuid4
from kafka import KafkaProducer

def generate_initial_switches():
    """
    Generate 20 initial switch records.
    We'll designate 4 parent switches and assign the rest to one of these.
    Each switch record has a unique switch_id and a parent_switch_id.
    """
    parent_switches = [str(uuid4()) for _ in range(4)]
    switches = []
    for _ in range(20):
        # 20% chance that a switch is its own parent
        is_parent = random.random() < 0.2
        switch_id = str(uuid4())
        parent_switch_id = switch_id if is_parent else random.choice(parent_switches)
        switch_data = {
            "switch_id": switch_id,
            "parent_switch_id": parent_switch_id,
            "bandwidth_usage": round(random.uniform(10, 1000), 2),  # in Mbps
            "packet_loss": round(random.uniform(0, 5), 2),           # in %
            "latency": round(random.uniform(1, 100), 2),             # in ms
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        switches.append(switch_data)
    return switches

def update_switches(switches):
    """
    Update each switch's metrics slightly to simulate real-time fluctuations.
    """
    for sw in switches:
        sw["bandwidth_usage"] = round(sw["bandwidth_usage"] * random.uniform(0.95, 1.05), 2)
        sw["packet_loss"] = round(sw["packet_loss"] * random.uniform(0.95, 1.05), 2)
        sw["latency"] = round(sw["latency"] * random.uniform(0.95, 1.05), 2)
        sw["timestamp"] = datetime.now(timezone.utc).isoformat()

def main():
    kafka_bootstrap_servers = "localhost:9092"  # Updated for local connectivity
    topic = "switch_data_topic"
    producer = KafkaProducer(
        bootstrap_servers=[kafka_bootstrap_servers],
        value_serializer=lambda v: json.dumps(v).encode("utf-8")
    )
    
    # Initialize our 20 switch records
    switches = generate_initial_switches()
    print("Initialized switches:")
    for sw in switches:
        print(sw)
    
    try:
        while True:
            update_switches(switches)
            for sw in switches:
                producer.send(topic, sw)
                print("Sent update for switch", sw["switch_id"])
            producer.flush()
            time.sleep(2)  # Wait 2 seconds before sending the next update batch
    except KeyboardInterrupt:
        print("Data generator stopped by user.")
    finally:
        producer.close()


if __name__ == '__main__':
    main()
