from app.repositories.sensor_repository import save_sensor_data
from app.schemas.sensor_schema import SensorData

async def process_sensor_data(data: dict):
    # Validate and parse data using Pydantic schema
    sensor_data = SensorData(**data)
    
    # Business logic: check for thresholds or data anomalies
    alert = None
    if sensor_data.temperature > 75:
        alert = {"message": "Temperature threshold exceeded!", "data": sensor_data.dict()}
    
    # Save data to Elasticsearch
    await save_sensor_data(sensor_data)
    
    return alert or {"message": "Data processed", "data": sensor_data.dict()}
