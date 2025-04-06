import asyncio
from elasticsearch import AsyncElasticsearch
from app.core.config import ES_HOST  # Ensure ES_HOST is set in your configuration

async def create_indices():
    es = AsyncElasticsearch(hosts=[ES_HOST])
    
    # Define index names
    alert_index = "alert_logs"
    switch_index = "switch_data"
    
    # Delete the indices if they exist
    if await es.indices.exists(index=alert_index):
        await es.indices.delete(index=alert_index)
        print(f"Deleted existing index: {alert_index}")
    if await es.indices.exists(index=switch_index):
        await es.indices.delete(index=switch_index)
        print(f"Deleted existing index: {switch_index}")
    
    # Create the alert_logs index with the mapping for alert documents
    alert_mapping = {
        "mappings": {
            "properties": {
                "timestamp": {"type": "date"},
                "switch_id": {"type": "keyword"},
                "parent_switch_id": {"type": "keyword"},
                "status": {"type": "keyword"},
                "bandwidth_usage": {"type": "float"},
                "packet_loss": {"type": "float"},
                "latency": {"type": "float"},
                "message": {"type": "text"}
            }
        }
    }
    await es.indices.create(index=alert_index, body=alert_mapping)
    print(f"Created index: {alert_index}")
    
    # Create the switch_data index with mapping for switch metrics
    switch_mapping = {
        "mappings": {
            "properties": {
                "timestamp": {"type": "date"},
                "switch_id": {"type": "keyword"},
                "parent_switch_id": {"type": "keyword"},
                "bandwidth_usage": {"type": "float"},
                "packet_loss": {"type": "float"},
                "latency": {"type": "float"}
            }
        }
    }
    await es.indices.create(index=switch_index, body=switch_mapping)
    print(f"Created index: {switch_index}")
    
    await es.close()

if __name__ == '__main__':
    asyncio.run(create_indices())
