import asyncio
from datetime import datetime, timezone
from elasticsearch import AsyncElasticsearch
from app.core.config import ES_HOST

async def seed_sensor_data():
    es = AsyncElasticsearch(hosts=[ES_HOST])
    index_name = "sensor_data"
    
    # Sample seed data – adjust values as needed for your use case.
    seed_data = [
        {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "count": 5,
            "avg_temperature": 70.0,
            "avg_humidity": 50.0,
            "min_temperature": 65.0,
            "max_temperature": 75.0,
            "alert": False,
            "raw_data": [
                {"temperature": 68.0, "humidity": 50.0, "timestamp": datetime.now(timezone.utc).isoformat()},
                {"temperature": 72.0, "humidity": 50.0, "timestamp": datetime.now(timezone.utc).isoformat()},
                {"temperature": 70.0, "humidity": 50.0, "timestamp": datetime.now(timezone.utc).isoformat()},
                {"temperature": 69.0, "humidity": 50.0, "timestamp": datetime.now(timezone.utc).isoformat()},
                {"temperature": 73.0, "humidity": 50.0, "timestamp": datetime.now(timezone.utc).isoformat()}
            ]
        },
        {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "count": 4,
            "avg_temperature": 80.0,
            "avg_humidity": 55.0,
            "min_temperature": 78.0,
            "max_temperature": 82.0,
            "alert": True,
            "raw_data": [
                {"temperature": 79.0, "humidity": 54.0, "timestamp": datetime.now(timezone.utc).isoformat()},
                {"temperature": 81.0, "humidity": 56.0, "timestamp": datetime.now(timezone.utc).isoformat()},
                {"temperature": 80.0, "humidity": 55.0, "timestamp": datetime.now(timezone.utc).isoformat()},
                {"temperature": 80.5, "humidity": 55.5, "timestamp": datetime.now(timezone.utc).isoformat()}
            ]
        }
    ]
    
    for record in seed_data:
        await es.index(index=index_name, document=record)
    print(f"Seeded {len(seed_data)} records into index '{index_name}'.")
    await es.close()

if __name__ == '__main__':
    asyncio.run(seed_sensor_data())
