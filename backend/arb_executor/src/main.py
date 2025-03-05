import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from backend.arb_executor.src.arb_executor import ArbExecutor
from backend.arb_executor.src.redis_listener import RedisListener
from backend.shared.logging import setup_logging
from backend.shared.redis_client import redis_client

setup_logging()

arb_executor = ArbExecutor(redis_client)
redis_listener = RedisListener(redis_client, arb_executor)

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
    title="Arbitrage Executor",
    description="Server which executes arbitrage opportunities.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "OK"}
