# app/api/endpoints/sensor.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def read_sensor_data():
    return {"message": "Sensor data endpoint"}
