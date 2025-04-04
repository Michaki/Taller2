# app/api/endpoints/sensor.py
from fastapi import APIRouter
from app.repositories.sensor_repository import get_all_sensor_data

router = APIRouter()

@router.get("/all")
async def read_all_sensor_data():
    data = await get_all_sensor_data()
    return {"data": data}