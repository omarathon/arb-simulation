import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from backend.arb_engine.src.arb_engine import ArbEngine
from backend.arb_engine.src.redis_listener import RedisListener
from backend.shared.logging import setup_logging
from backend.shared.redis_client import redis_client

setup_logging()

arb_engine = ArbEngine(redis_client)
redis_listener = RedisListener(redis_client, arb_engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(redis_listener.listen())
    try:
        yield
    finally:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

app = FastAPI(
    title="Arbitrage Engine",
    description="Server which detects arbitrage opportunities from odds updates and sends bets to execute them.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "OK"}