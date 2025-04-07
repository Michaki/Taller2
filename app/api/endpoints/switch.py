from fastapi import APIRouter, HTTPException
from app.repositories.switch_repository import (
    get_overall_metrics,
    get_alert_count,
    get_alert_logs,
    get_alert_insights,
    clear_all_documents,
    get_topology,
    get_all,
    get_aggregated_bandwidth,
    get_switch_state_summary
)

router = APIRouter()

@router.get("/")
async def root():
    return {"message": "Welcome to the Network Switch Monitoring API!"}

@router.get("/aggregated")
async def aggregated_switches():
    try:
        state_summary = await get_switch_state_summary()
        timestamps, avg_bandwidth_trend = await get_aggregated_bandwidth()
        overall_metrics = await get_overall_metrics()
        alert_count = await get_alert_count()
        
        # Return only the necessary data for the dashboard
        return {
            "state_summary": state_summary,          
            "alert_count": alert_count,              
            "timestamps": timestamps,                
            "avg_bandwidth_trend": avg_bandwidth_trend,
            "overall_metrics": overall_metrics       
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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