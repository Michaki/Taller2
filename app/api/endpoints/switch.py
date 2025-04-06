from fastapi import APIRouter
from app.repositories.switch_repository import (
    get_all_aggregated_switch_data,
    get_aggregated_switch_data_count,
    get_alert_logs,
    get_alert_insights
)

router = APIRouter()

@router.get("/")
async def root():
    return {"message": "Welcome to the Network Switch Monitoring API!"}

@router.get("/aggregated")
async def aggregated_switches():
    records = await get_all_aggregated_switch_data()
    count = await get_aggregated_switch_data_count()
    return {"count": count, "records": records}

@router.get("/alerts")
async def switch_alerts():
    logs = await get_alert_logs()
    return {"logs": logs}

@router.get("/alerts/insights")
async def switch_alert_insights():
    insights = await get_alert_insights()
    return {"insights": insights}
