import asyncio
from elasticsearch import AsyncElasticsearch
from app.core.config import ES_HOST  # Make sure your config loads ES_HOST from .env or similar

async def create_sensor_index():
    es = AsyncElasticsearch(hosts=[ES_HOST])
    index_name = "sensor_data"

    # Check if the index exists
    exists = await es.indices.exists(index=index_name)
    if not exists:
        mapping = {
            "mappings": {
                "properties": {
                    "temperature": {"type": "float"},
                    "humidity": {"type": "float"},
                    "timestamp": {"type": "date"}
                }
            }
        }
        # Create the index with the specified mapping
        await es.indices.create(index=index_name, body=mapping)
        print(f"Index '{index_name}' created successfully.")
    else:
        print(f"Index '{index_name}' already exists.")

    await es.close()

if __name__ == "__main__":
    asyncio.run(create_sensor_index())
