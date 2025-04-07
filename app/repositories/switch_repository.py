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

async def get_all(): 
    # Count the number of documents in the switch_data index
    result = await es.count(index="switch_data")
    count = result["count"]
    return count



async def get_aggregated_switch_data_count():
    result = await es.search(
        index="switch_data",
        body={
            "size": 0,
            "aggs": {
                "distinct_switches": {
                    "cardinality": {
                        "field": "switch_id"
                    }
                }
            }
        }
    )
    return result["aggregations"]["distinct_switches"]["value"]

async def get_aggregated_bandwidth():
    """
    Performs an aggregation query on the "switch_data" index
    to compute the average bandwidth usage grouped by a fixed time interval (e.g., every 5 minutes).
    """
    query = {
        "size": 0,
        "aggs": {
            "bandwidth_over_time": {
                "date_histogram": {
                    "field": "timestamp",
                    "fixed_interval": "5m"
                },
                "aggs": {
                    "avg_bandwidth": {
                        "avg": {"field": "bandwidth_usage"}
                    }
                }
            }
        }
    }
    result = await es.search(index="switch_data", body=query)
    buckets = result["aggregations"]["bandwidth_over_time"]["buckets"]
    timestamps = [bucket["key_as_string"] for bucket in buckets]
    avg_bandwidth_values = [bucket["avg_bandwidth"]["value"] for bucket in buckets]
    return timestamps, avg_bandwidth_values



async def get_alert_logs():
    result = await es.search(index="alert_logs", body={"query": {"match_all": {}}})
    logs = [hit["_source"] for hit in result["hits"]["hits"]]
    return logs

async def get_alert_logs_count():
    result = await es.count(index="alert_logs")
    count = result["count"]
    return count

async def clear_all_documents():
    """
    Deletes all documents from the 'alert_logs' and 'switch_data' indices without deleting the indexes.
    """
    # Delete all documents from the alert_logs index
    await es.delete_by_query(index="alert_logs", body={"query": {"match_all": {}}})
    # Delete all documents from the switch_data index
    await es.delete_by_query(index="switch_data", body={"query": {"match_all": {}}})


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


async def get_topology():
    """
    Constructs the topology from the stored switch data.
    Returns a dictionary with 'nodes' and 'edges'.
    """
    # Query the switch_data index to get all documents.
    result = await es.search(index="switch_data", body={"query": {"match_all": {}}}, size=1000)
    hits = result["hits"]["hits"]
    
    nodes = {}
    edges = []
    
    for hit in hits:
        doc = hit["_source"]
        sid = doc.get("switch_id")
        pid = doc.get("parent_switch_id")
        # Create or update node; note the property name "nodeState"
        if sid:
            nodes[sid] = {"id": sid, "label": sid, "nodeState": doc.get("status", "unknown")}
        # Create an edge if there's a parent that is different than the switch id.
        if pid and pid != sid:
            edges.append({"id": f"{pid}_{sid}", "source": pid, "target": sid})
    
    return {"nodes": list(nodes.values()), "edges": edges}
