# app/api/endpoints/sensor.py
from fastapi import APIRouter
from app.repositories.sensor_repository import get_all_sensor_data, get_all_aggregated_sensor_data, get_aggregated_sensor_data_count

router = APIRouter()

@router.get("/all")
async def read_all_sensor_data():
    data = await get_all_sensor_data()
    return {"data": data}

@router.get("/aggregated")
async def read_aggregated_sensor_data():
    records = await get_all_aggregated_sensor_data()
    count = await get_aggregated_sensor_data_count()
    return {"count": count, "records": records}