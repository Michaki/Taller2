from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import switch, websocket
import asyncio
from contextlib import asynccontextmanager
from app.streams.stream_consumer import consume_topics_for_websocket

origins = ["http://localhost:5173"]

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Launch the Kafka consumer (reading from both topics) as a background task.
    consumer_task = asyncio.create_task(consume_topics_for_websocket())
    yield  # The app runs while yielding here.
    consumer_task.cancel()
    try:
        await consumer_task
    except asyncio.CancelledError:
        pass

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(switch.router, prefix="/switch")
app.include_router(websocket.router, prefix="/ws")

if __name__ == '__main__':
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
