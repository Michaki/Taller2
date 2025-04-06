import asyncio
from elasticsearch import AsyncElasticsearch
from app.core.config import ES_HOST  # Ensure ES_HOST is set in your config

async def clear_and_create_sensor_index():
    es = AsyncElasticsearch(hosts=[ES_HOST])
    index_name = "sensor_data"
    
    # Delete the index if it exists
    if await es.indices.exists(index=index_name):
        await es.indices.delete(index=index_name)
        print(f"Deleted existing index: {index_name}")
    
    # Create the index with the updated mapping
    mapping = {
        "mappings": {
            "properties": {
                "timestamp": {"type": "date"},
                "count": {"type": "integer"},
                "avg_temperature": {"type": "float"},
                "avg_humidity": {"type": "float"},
                "min_temperature": {"type": "float"},
                "max_temperature": {"type": "float"},
                "alert": {"type": "boolean"},
                "raw_data": {"type": "nested"}  # or "object" if you prefer
            }
        }
    }
    
    await es.indices.create(index=index_name, body=mapping)
    print(f"Created index: {index_name} with mapping.")
    await es.close()

if __name__ == '__main__':
    asyncio.run(clear_and_create_sensor_index())
