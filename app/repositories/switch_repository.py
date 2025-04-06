from elasticsearch import AsyncElasticsearch
from app.core.config import ES_HOST

es = AsyncElasticsearch(hosts=[ES_HOST])

async def save_alert_log(message: dict):
    """Persist an alert log document to Elasticsearch."""
    await es.index(index="alert_logs", body=message)

async def save_switch_data(message: dict):
    """Persist a healthy switch document to Elasticsearch."""
    await es.index(index="switch_data", body=message)

async def get_all_aggregated_switch_data():
    result = await es.search(index="switch_data", body={"query": {"match_all": {}}})
    records = [hit["_source"] for hit in result["hits"]["hits"]]
    return records

async def get_aggregated_switch_data_count():
    result = await es.count(index="switch_data")
    return result["count"]

async def get_alert_logs():
    result = await es.search(index="alert_logs", body={"query": {"match_all": {}}})
    logs = [hit["_source"] for hit in result["hits"]["hits"]]
    return logs


async def get_alert_insights():
    """
    Return insights from the alert_logs index:
      - A date histogram (bucketed by 5 minutes) of alert counts in the last hour.
      - A terms aggregation for the top 10 parent_switch_id values by alert count.
    """
    query = {
        "size": 0,
        "query": {
            "range": {
                "timestamp": {"gte": "now-1h"}
            }
        },
        "aggs": {
            "alerts_over_time": {
                "date_histogram": {
                    "field": "timestamp",
                    "fixed_interval": "5m",
                    "min_doc_count": 0
                },
                "aggs": {
                    "alert_count": {"value_count": {"field": "switch_id"}}
                }
            },
            "alerts_by_parent": {
                "terms": {
                    "field": "parent_switch_id",
                    "size": 10
                }
            }
        }
    }
    result = await es.search(index="alert_logs", body=query)
    return result["aggregations"]