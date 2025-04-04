from elasticsearch import AsyncElasticsearch
from app.core.config import ES_HOST
from app.schemas.sensor_schema import SensorData

es = AsyncElasticsearch(hosts=[ES_HOST])

async def save_sensor_data(sensor_data: SensorData):
    doc = sensor_data.dict()
    await es.index(index="sensor_data", document=doc)
