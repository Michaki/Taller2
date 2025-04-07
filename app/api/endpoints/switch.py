from fastapi import APIRouter, HTTPException
from app.repositories.switch_repository import (
    get_all_aggregated_switch_data,
    get_aggregated_switch_data_count,
    get_alert_logs,
    get_alert_insights,
    clear_all_documents,
    get_topology,
    get_all,
    get_alert_logs_count,
    get_aggregated_bandwidth
)

router = APIRouter()

@router.get("/")
async def root():
    return {"message": "Welcome to the Network Switch Monitoring API!"}

@router.get("/aggregated")
async def aggregated_switches():
    # Fetch healthy switch data
    healthy_records = await get_all_aggregated_switch_data()
    healthy_count = await get_aggregated_switch_data_count()
    # Fetch alert logs (we can simply count them rather than return full details)
    alert_logs = await get_alert_logs()
    alert_count = await get_alert_logs_count()
    # Fetch aggregated bandwidth data
    timestamps, bandwidth_data = await get_aggregated_bandwidth()
    
    return {
        "healthy_count": healthy_count,
        "healthy_records": healthy_records,
        "alert_logs": alert_logs,
        "alert_count": alert_count,
        "avg_bandwidth": bandwidth_data,
        "timestamps": timestamps
    }

@router.get("/all")
async def all_switches():
    """
    Fetch all documents from the switch_data index.
    """
    try:
        records = await get_all()
        return {"records": records}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/alerts")
async def switch_alerts():
    logs = await get_alert_logs()
    return {"logs": logs}

@router.get("/topology")
async def topology():
    try:
        topo = await get_topology()
        return topo
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/alerts/insights")
async def switch_alert_insights():
    insights = await get_alert_insights()
    return {"insights": insights}

# Delete all elasticsearch documents
@router.delete("/clear")
async def clear_database_documents():
    """
    Deletes all documents from the 'alert_logs' and 'switch_data' indices.
    This is for testing purposes only.
    """
    try:
        await clear_all_documents()
        return {"message": "All documents cleared from alert_logs and switch_data indices."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))