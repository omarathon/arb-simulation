from fastapi import FastAPI
from backend.gateway.src.websocket_handler import websocket_endpoint
from backend.gateway.src.redis_listener import RedisListener
from contextlib import asynccontextmanager
import asyncio
from backend.shared.logging import setup_logging
from backend.shared.redis_client import redis_client

setup_logging()

redis_listener = RedisListener(redis_client)

@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(redis_listener.listen())
    yield
    task.cancel()

app = FastAPI(
    title="Gateway API",
    description="Gateway API for arbitrage bot backend.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "OK"}

app.add_api_websocket_route("/ws", websocket_endpoint)
