import random
import time
import json
import os
from datetime import datetime, timezone
from uuid import uuid4
from kafka import KafkaProducer

# Umbrales y multiplicadores
BANDWIDTH_THRESHOLD = 800      # Mbps
PACKET_LOSS_THRESHOLD = 2      # %
LATENCY_THRESHOLD = 80         # ms

BANDWIDTH_UNHEALTHY_MULTIPLIER = 1.2
PACKET_LOSS_UNHEALTHY_MULTIPLIER = 1.5
LATENCY_UNHEALTHY_MULTIPLIER = 1.2

SWITCHES_FILE = "switches.json"  # Archivo persistente

def generate_initial_switches():
    """
    Genera 20 switches: 16 en modo 'healthy' y 4 en modo 'faulty'.
    """
    parent_switches = [str(uuid4()) for _ in range(4)]
    modes = ['healthy'] * 16 + ['faulty'] * 4
    random.shuffle(modes)

    switches = []
    for mode in modes:
        switch_id = str(uuid4())
        parent_switch_id = switch_id if random.random() < 0.2 else random.choice(parent_switches)

        if mode == 'healthy':
            bandwidth = round(random.uniform(0, BANDWIDTH_THRESHOLD * 0.9), 2)
            packet_loss = round(random.uniform(0, PACKET_LOSS_THRESHOLD * 0.9), 2)
            latency = round(random.uniform(0, LATENCY_THRESHOLD * 0.9), 2)
        else:
            status_type = random.choice(['warning', 'unhealthy'])
            bandwidth = round(random.uniform(0, BANDWIDTH_THRESHOLD * 0.9), 2)
            packet_loss = round(random.uniform(0, PACKET_LOSS_THRESHOLD * 0.9), 2)
            latency = round(random.uniform(0, LATENCY_THRESHOLD * 0.9), 2)

            metric = random.choice(['bandwidth', 'packet_loss', 'latency'])
            if metric == 'bandwidth':
                bandwidth = round(random.uniform(
                    BANDWIDTH_THRESHOLD * (1.01 if status_type == 'warning' else BANDWIDTH_UNHEALTHY_MULTIPLIER * 1.01),
                    BANDWIDTH_THRESHOLD * (BANDWIDTH_UNHEALTHY_MULTIPLIER * 0.99 if status_type == 'warning' else BANDWIDTH_UNHEALTHY_MULTIPLIER * 1.5)
                ), 2)
            elif metric == 'packet_loss':
                packet_loss = round(random.uniform(
                    PACKET_LOSS_THRESHOLD * (1.01 if status_type == 'warning' else PACKET_LOSS_UNHEALTHY_MULTIPLIER * 1.01),
                    PACKET_LOSS_THRESHOLD * (PACKET_LOSS_UNHEALTHY_MULTIPLIER * 0.99 if status_type == 'warning' else PACKET_LOSS_UNHEALTHY_MULTIPLIER * 1.5)
                ), 2)
            else:  # latency
                latency = round(random.uniform(
                    LATENCY_THRESHOLD * (1.01 if status_type == 'warning' else LATENCY_UNHEALTHY_MULTIPLIER * 1.01),
                    LATENCY_THRESHOLD * (LATENCY_UNHEALTHY_MULTIPLIER * 0.99 if status_type == 'warning' else LATENCY_UNHEALTHY_MULTIPLIER * 1.5)
                ), 2)

        switches.append({
            "switch_id": switch_id,
            "parent_switch_id": parent_switch_id,
            "bandwidth_usage": bandwidth,
            "packet_loss": packet_loss,
            "latency": latency,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "mode": mode
        })
    return switches

def load_or_generate_switches():
    if os.path.exists(SWITCHES_FILE):
        with open(SWITCHES_FILE, "r") as f:
            switches = json.load(f)
            print("Switches cargados desde archivo.")
            return switches
    else:
        switches = generate_initial_switches()
        with open(SWITCHES_FILE, "w") as f:
            json.dump(switches, f, indent=2)
        print("Switches generados y guardados.")
        return switches

def update_switches(switches):
    for sw in switches:
        mode = sw.get("mode", "healthy")

        if mode == 'healthy':
            sw["bandwidth_usage"] = round(random.uniform(0, BANDWIDTH_THRESHOLD * 0.9), 2)
            sw["packet_loss"]     = round(random.uniform(0, PACKET_LOSS_THRESHOLD * 0.9), 2)
            sw["latency"]         = round(random.uniform(0, LATENCY_THRESHOLD * 0.9), 2)
        else:
            status_type = random.choice(['warning', 'unhealthy'])
            bw = round(random.uniform(0, BANDWIDTH_THRESHOLD * 0.9), 2)
            pl = round(random.uniform(0, PACKET_LOSS_THRESHOLD * 0.9), 2)
            lt = round(random.uniform(0, LATENCY_THRESHOLD * 0.9), 2)

            metric = random.choice(['bandwidth', 'packet_loss', 'latency'])
            if metric == 'bandwidth':
                bw = round(random.uniform(
                    BANDWIDTH_THRESHOLD * (1.01 if status_type == 'warning' else BANDWIDTH_UNHEALTHY_MULTIPLIER * 1.01),
                    BANDWIDTH_THRESHOLD * (BANDWIDTH_UNHEALTHY_MULTIPLIER * 0.99 if status_type == 'warning' else BANDWIDTH_UNHEALTHY_MULTIPLIER * 1.5)
                ), 2)
            elif metric == 'packet_loss':
                pl = round(random.uniform(
                    PACKET_LOSS_THRESHOLD * (1.01 if status_type == 'warning' else PACKET_LOSS_UNHEALTHY_MULTIPLIER * 1.01),
                    PACKET_LOSS_THRESHOLD * (PACKET_LOSS_UNHEALTHY_MULTIPLIER * 0.99 if status_type == 'warning' else PACKET_LOSS_UNHEALTHY_MULTIPLIER * 1.5)
                ), 2)
            else:  # latency
                lt = round(random.uniform(
                    LATENCY_THRESHOLD * (1.01 if status_type == 'warning' else LATENCY_UNHEALTHY_MULTIPLIER * 1.01),
                    LATENCY_THRESHOLD * (LATENCY_UNHEALTHY_MULTIPLIER * 0.99 if status_type == 'warning' else LATENCY_UNHEALTHY_MULTIPLIER * 1.5)
                ), 2)

            sw["bandwidth_usage"] = bw
            sw["packet_loss"]     = pl
            sw["latency"]         = lt

        sw["timestamp"] = datetime.now(timezone.utc).isoformat()

def main():
    kafka_bootstrap_servers = "kafka:9092"
    topic = "switch_data_topic"

    producer = KafkaProducer(
        bootstrap_servers=[kafka_bootstrap_servers],
        value_serializer=lambda v: json.dumps(v).encode("utf-8")
    )
    
    switches = load_or_generate_switches()

    try:
        while True:
            update_switches(switches)
            for sw in switches:
                producer.send(topic, sw)
                print(f"Sent update for switch {sw['switch_id']} (mode={sw['mode']})")
            producer.flush()
            time.sleep(2)
    except KeyboardInterrupt:
        print("Data generator stopped.")
    finally:
        producer.close()

if __name__ == '__main__':
    main()
