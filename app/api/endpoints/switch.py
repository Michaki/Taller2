from fastapi import APIRouter
from app.services.alert_service import get_alert_logs
from app.repositories.switch_repository import get_aggregated_switch_data_count, get_all_aggregated_switch_data

router = APIRouter()

@router.get("/")
async def root():
    return {"message": "Welcome to the Network Switch Monitoring API!"}

@router.get("/aggregated")
async def aggregated_switches():
    records = await get_all_aggregated_switch_data()
    count = await get_aggregated_switch_data_count()
    return {"count": count, "records": records}

@router.get("/logs")
async def switch_logs():
    return {"logs": get_alert_logs()}