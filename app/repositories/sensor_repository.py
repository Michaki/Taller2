from elasticsearch import AsyncElasticsearch
from app.core.config import ES_HOST
from app.schemas.sensor_schema import SensorData

es = AsyncElasticsearch(hosts=[ES_HOST])

async def save_sensor_data(sensor_data: SensorData):
    doc = sensor_data.model_dump()
    await es.index(index="sensor_data", document=doc)

async def get_all_sensor_data():
    es = AsyncElasticsearch(hosts=[ES_HOST])
    # Use a match_all query to retrieve all documents
    query = {"query": {"match_all": {}}}
    response = await es.search(index="sensor_data", body=query)
    await es.close()
    # The documents are in response['hits']['hits']
    return response['hits']['hits']