from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import switch, websocket
import asyncio
from contextlib import asynccontextmanager
from app.streams.stream_consumer import consume_switch_data
from app.repositories.switch_repository import get_recent_alert_logs_from_es  # Utility to fetch recent alerts from ES

# Configure allowed origins for CORS
origins = [
    "http://localhost:5173",  
]

# Global in-memory alert buffer that holds recent alerts for real-time notification
alert_buffer = []

# Refresh interval (in seconds) for the in-memory alert buffer
REFRESH_INTERVAL = 60  # For example, every 60 seconds

async def refresh_alert_buffer_periodically():
    """
    Periodically refresh (or clear) the in-memory alert buffer.
    Option 1: Fetch recent alert logs from Elasticsearch and update the buffer.
    Option 2: Simply clear the buffer if that meets your needs.
    """
    global alert_buffer
    while True:
        try:
            # Option 1: Refresh the buffer with recent alerts from ES.
            # This assumes you have stored alerts in an Elasticsearch index called "alert_logs".
            alert_buffer = await get_recent_alert_logs_from_es(time_window=300)
            print("Alert buffer refreshed from Elasticsearch")
            
            # Option 2: Alternatively, simply clear the buffer to avoid memory buildup.
            # alert_buffer.clear()
            # print("Alert buffer cleared.")
            
        except Exception as e:
            print(f"Error refreshing alert buffer: {e}")
        await asyncio.sleep(REFRESH_INTERVAL)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: launch both the Kafka consumer and the refresh task as background tasks.
    consumer_task = asyncio.create_task(consume_switch_data())
    refresh_task = asyncio.create_task(refresh_alert_buffer_periodically())
    yield  # The app runs while yielding here
    # Shutdown: cancel both background tasks gracefully.
    consumer_task.cancel()
    refresh_task.cancel()
    try:
        await consumer_task
    except asyncio.CancelledError:
        pass
    try:
        await refresh_task
    except asyncio.CancelledError:
        pass

app = FastAPI(lifespan=lifespan)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include REST and WebSocket routes
app.include_router(switch.router, prefix="/switch")
app.include_router(websocket.router, prefix="/ws")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
