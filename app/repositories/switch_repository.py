from elasticsearch import AsyncElasticsearch
from app.core.config import ES_HOST

es = AsyncElasticsearch(hosts=[ES_HOST])

async def save_aggregated_switch_data(aggregated_data: dict):
    await es.index(index="aggregated_switch_data", document=aggregated_data)

async def get_all_aggregated_switch_data():
    query = {"query": {"match_all": {}}}
    response = await es.search(index="aggregated_switch_data", body=query)
    return response['hits']['hits']

async def get_aggregated_switch_data_count():
    response = await es.count(index="aggregated_switch_data")
    return response['count']

async def get_recent_alert_logs_from_es(time_window: int = 300):
    """
    Query Elasticsearch to fetch alert logs from the past `time_window` seconds.
    Adjust the index and query as needed.
    """
    query = {
        "query": {
            "range": {
                "timestamp": {
                    "gte": f"now-{time_window}s"
                }
            }
        },
        "sort": [{"timestamp": {"order": "desc"}}]
    }
    result = await es.search(index="alert_logs", body=query)
    hits = result["hits"]["hits"]
    # Extract the _source field from each hit
    logs = [hit["_source"] for hit in hits]
    return logs