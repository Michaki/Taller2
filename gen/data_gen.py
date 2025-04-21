import random
import time
import json
from datetime import datetime, timezone
from uuid import uuid4
from kafka import KafkaProducer

# Umbrales y multiplicadores (deben coincidir con los de kafka_stream.py)
BANDWIDTH_THRESHOLD = 800      # Mbps
PACKET_LOSS_THRESHOLD = 2      # %
LATENCY_THRESHOLD = 80         # ms

BANDWIDTH_UNHEALTHY_MULTIPLIER = 1.2
PACKET_LOSS_UNHEALTHY_MULTIPLIER = 1.5
LATENCY_UNHEALTHY_MULTIPLIER = 1.2

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
            # Todos los valores por debajo de los umbrales
            bandwidth = round(random.uniform(0, BANDWIDTH_THRESHOLD * 0.9), 2)
            packet_loss = round(random.uniform(0, PACKET_LOSS_THRESHOLD * 0.9), 2)
            latency = round(random.uniform(0, LATENCY_THRESHOLD * 0.9), 2)
        else:
            # En modo faulty, al menos una métrica cruza un umbral
            # Elegimos un tipo de fallo: 'warning' o 'unhealthy'
            status_type = random.choice(['warning', 'unhealthy'])
            # Métricas base sanas
            bandwidth = round(random.uniform(0, BANDWIDTH_THRESHOLD * 0.9), 2)
            packet_loss = round(random.uniform(0, PACKET_LOSS_THRESHOLD * 0.9), 2)
            latency = round(random.uniform(0, LATENCY_THRESHOLD * 0.9), 2)

            # Escogemos una métrica al azar para sobrepasar
            metric = random.choice(['bandwidth', 'packet_loss', 'latency'])
            if metric == 'bandwidth':
                if status_type == 'warning':
                    bandwidth = round(random.uniform(BANDWIDTH_THRESHOLD * 1.01, BANDWIDTH_THRESHOLD * BANDWIDTH_UNHEALTHY_MULTIPLIER * 0.99), 2)
                else:
                    bandwidth = round(random.uniform(BANDWIDTH_THRESHOLD * BANDWIDTH_UNHEALTHY_MULTIPLIER * 1.01, BANDWIDTH_THRESHOLD * BANDWIDTH_UNHEALTHY_MULTIPLIER * 1.5), 2)
            elif metric == 'packet_loss':
                if status_type == 'warning':
                    packet_loss = round(random.uniform(PACKET_LOSS_THRESHOLD * 1.01, PACKET_LOSS_THRESHOLD * PACKET_LOSS_UNHEALTHY_MULTIPLIER * 0.99), 2)
                else:
                    packet_loss = round(random.uniform(PACKET_LOSS_THRESHOLD * PACKET_LOSS_UNHEALTHY_MULTIPLIER * 1.01, PACKET_LOSS_THRESHOLD * PACKET_LOSS_UNHEALTHY_MULTIPLIER * 1.5), 2)
            else:  # latency
                if status_type == 'warning':
                    latency = round(random.uniform(LATENCY_THRESHOLD * 1.01, LATENCY_THRESHOLD * LATENCY_UNHEALTHY_MULTIPLIER * 0.99), 2)
                else:
                    latency = round(random.uniform(LATENCY_THRESHOLD * LATENCY_UNHEALTHY_MULTIPLIER * 1.01, LATENCY_THRESHOLD * LATENCY_UNHEALTHY_MULTIPLIER * 1.5), 2)

        switches.append({
            "switch_id": switch_id,
            "parent_switch_id": parent_switch_id,
            "bandwidth_usage": bandwidth,
            "packet_loss": packet_loss,
            "latency": latency,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            # opcional, te sirve para debug
            "mode": mode
        })
    return switches

def update_switches(switches):
    """
    Ajusta ligeramente las métricas en cada paso de tiempo,
    manteniendo el comportamiento definido por el modo inicial.
    """
    for sw in switches:
        mode = sw.get("mode", "healthy")

        if mode == 'healthy':
            # Fluctuaciones ligeras dentro de rango saludable
            sw["bandwidth_usage"] = round(random.uniform(0, BANDWIDTH_THRESHOLD * 0.9), 2)
            sw["packet_loss"]     = round(random.uniform(0, PACKET_LOSS_THRESHOLD * 0.9), 2)
            sw["latency"]         = round(random.uniform(0, LATENCY_THRESHOLD * 0.9), 2)
        else:
            # Faulty: generamos warning o unhealthy de nuevo
            status_type = random.choice(['warning', 'unhealthy'])
            # Base aleatoria en rango healthy
            bw = round(random.uniform(0, BANDWIDTH_THRESHOLD * 0.9), 2)
            pl = round(random.uniform(0, PACKET_LOSS_THRESHOLD * 0.9), 2)
            lt = round(random.uniform(0, LATENCY_THRESHOLD * 0.9), 2)

            metric = random.choice(['bandwidth', 'packet_loss', 'latency'])
            if metric == 'bandwidth':
                if status_type == 'warning':
                    bw = round(random.uniform(BANDWIDTH_THRESHOLD * 1.01, BANDWIDTH_THRESHOLD * BANDWIDTH_UNHEALTHY_MULTIPLIER * 0.99), 2)
                else:
                    bw = round(random.uniform(BANDWIDTH_THRESHOLD * BANDWIDTH_UNHEALTHY_MULTIPLIER * 1.01, BANDWIDTH_THRESHOLD * BANDWIDTH_UNHEALTHY_MULTIPLIER * 1.5), 2)
            elif metric == 'packet_loss':
                if status_type == 'warning':
                    pl = round(random.uniform(PACKET_LOSS_THRESHOLD * 1.01, PACKET_LOSS_THRESHOLD * PACKET_LOSS_UNHEALTHY_MULTIPLIER * 0.99), 2)
                else:
                    pl = round(random.uniform(PACKET_LOSS_THRESHOLD * PACKET_LOSS_UNHEALTHY_MULTIPLIER * 1.01, PACKET_LOSS_THRESHOLD * PACKET_LOSS_UNHEALTHY_MULTIPLIER * 1.5), 2)
            else:  # latency
                if status_type == 'warning':
                    lt = round(random.uniform(LATENCY_THRESHOLD * 1.01, LATENCY_THRESHOLD * LATENCY_UNHEALTHY_MULTIPLIER * 0.99), 2)
                else:
                    lt = round(random.uniform(LATENCY_THRESHOLD * LATENCY_UNHEALTHY_MULTIPLIER * 1.01, LATENCY_THRESHOLD * LATENCY_UNHEALTHY_MULTIPLIER * 1.5), 2)

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
    
    switches = generate_initial_switches()
    print("Initialized switches:")
    for sw in switches:
        print(sw)
    
    try:
        while True:
            update_switches(switches)
            for sw in switches:
                producer.send(topic, sw)
                print(f"Sent update for switch {sw['switch_id']} (mode={sw['mode']})")
            producer.flush()
            time.sleep(2)
    except KeyboardInterrupt:
        print("Data generator stopped by user.")
    finally:
        producer.close()

if __name__ == '__main__':
    main()
