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
