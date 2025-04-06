# Example in Python using Pydantic
from pydantic import BaseModel
from typing import List
from datetime import datetime

class StatusEnum(str):
    HEALTHY = "healthy"
    WARNING = "warning"
    UNHEALTHY = "unhealthy"

    def __str__(self):
        return self.value

class AggregatedSwitchData(BaseModel):
    id: str  # Elasticsearch _id
    timestamp: datetime
    parent_switch_id: str
    count: int
    avg_bandwidth: float
    avg_packet_loss: float
    avg_latency: float
    status: StatusEnum
    alert: bool
    raw_data: List[dict]
