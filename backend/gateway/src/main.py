from fastapi import FastAPI
from backend.gateway.src.websocket_handler import websocket_endpoint
from backend.gateway.src.redis_listener import RedisListener
from contextlib import asynccontextmanager
import asyncio

# Initialize Redis listener instance
redis_listener = RedisListener()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Start Redis listener properly as an async task on app startup."""
    task = asyncio.create_task(redis_listener.listen())  # ✅ Now correctly running as a coroutine
    print("✅ Gateway Redis listener started...")
    
    yield  # Wait until shutdown
    
    task.cancel()  # Stop the background task when shutting down
    print("❌ Gateway shutting down...")

app = FastAPI(
    title="Gateway API",
    description="Gateway API for arbitrage bot backend.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan  # ✅ Attach lifespan to FastAPI app
)

@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "OK"}

app.add_api_websocket_route("/ws", websocket_endpoint)
