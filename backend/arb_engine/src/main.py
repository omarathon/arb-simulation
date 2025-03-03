import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from backend.arb_engine.src.arb_engine import ArbEngine
from backend.arb_engine.src.redis_listener import RedisListener

# Initialize ArbEngine and RedisListener
arb_engine = ArbEngine()
redis_listener = RedisListener(arb_engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manages startup and shutdown of background tasks."""
    task = asyncio.create_task(redis_listener.listen())

    print("🚀 Redis Listener started.")

    try:
        yield
    finally:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass  # Expected on shutdown

        print("🛑 Redis Listener shut down.")

app = FastAPI(
    title="Arbitrage Engine API",
    description="API for detecting arbitrage opportunities from odds updates and sending bets to execute them.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

@app.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint."""
    return {"status": "OK"}
