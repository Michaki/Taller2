# app/schemas/sensor_schema.py
from pydantic import BaseModel, Field

class SensorData(BaseModel):
    temperature: float = Field(..., description="Temperature reading from sensor")
    humidity: float = Field(None, description="Optional humidity reading")