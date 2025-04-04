from fastapi import FastAPI
from app.api.endpoints import sensor, websocket

app = FastAPI()

# Include REST and WebSocket routes
app.include_router(sensor.router, prefix="/sensors")
app.include_router(websocket.router, prefix="/ws")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
