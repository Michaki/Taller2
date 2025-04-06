from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import sensor, websocket
import asyncio
from contextlib import asynccontextmanager
from app.streams.stream_consumer import consume_sensor_data

origins = [
    "http://localhost:5173",  
]

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: launch the Kafka consumer as a background task
    consumer_task = asyncio.create_task(consume_sensor_data())
    yield  # The app runs while yielding here
    # Shutdown: cancel the Kafka consumer task
    consumer_task.cancel()
    try:
        await consumer_task
    except asyncio.CancelledError:
        pass

app = FastAPI(lifespan=lifespan)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,           # Allow these origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include REST and WebSocket routes
app.include_router(sensor.router, prefix="/sensors")
app.include_router(websocket.router, prefix="/ws")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
