from elasticsearch import AsyncElasticsearch
from app.core.config import ES_HOST
from app.schemas.sensor_schema import SensorData

es = AsyncElasticsearch(hosts=[ES_HOST])

async def save_sensor_data(sensor_data: SensorData):
    doc = sensor_data.model_dump()
    await es.index(index="sensor_data", document=doc)

async def save_aggregated_sensor_data(aggregated_data: dict):
    await es.index(index="aggregated_sensor_data", document=aggregated_data)

async def get_all_sensor_data():
    es = AsyncElasticsearch(hosts=[ES_HOST])
    # Use a match_all query to retrieve all documents
    query = {"query": {"match_all": {}}}
    response = await es.search(index="sensor_data", body=query)
    await es.close()
    # The documents are in response['hits']['hits']
    return response['hits']['hits']

async def get_aggregated_sensor_data_count():
    response = await es.count(index="aggregated_sensor_data")
    return response['count']

async def get_all_aggregated_sensor_data():
    query = {"query": {"match_all": {}}}
    response = await es.search(index="aggregated_sensor_data", body=query)
    return response['hits']['hits']