# seeds/seed_sensor_data.py
import asyncio
from datetime import datetime, timezone
from elasticsearch import AsyncElasticsearch
from app.core.config import ES_HOST

async def seed_sensor_data():
    es = AsyncElasticsearch(hosts=[ES_HOST])
    index_name = "sensor_data"

    # Define a list of seed sensor data records
    seed_data = [
        {"temperature": 72.5, "humidity": 45.0, "timestamp": datetime.now(timezone.utc)},
        {"temperature": 80.0, "humidity": 50.0, "timestamp": datetime.now(timezone.utc)},
        {"temperature": 68.0, "humidity": 55.0, "timestamp": datetime.now(timezone.utc)},
    ]

    for record in seed_data:
        await es.index(index=index_name, document=record)
    print(f"Seeded {len(seed_data)} sensor data records into the '{index_name}' index.")

    await es.close()

if __name__ == "__main__":
    asyncio.run(seed_sensor_data())
